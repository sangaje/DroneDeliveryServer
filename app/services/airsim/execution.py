"""This module launchs AirSim simulation with specified configurations."""

import time

from cosysairsim import MultirotorState

from app.models.drone import DroneStatus
from app.models.order import Order
from app.services.controller.database import init_db
from app.services.controller.drone_service import create_drone
from app.services.controller.order_service import create_order, get_order
from app.utils.airsimutils import (
    Drone,
    connect_client,
    create_drones_list,
    disconnect_client,
    is_conneted,
    sim_reset,
)

from .config import AirSimConfig

# Global, process-wide AirSim configuration for the current session.
_airsim_config: AirSimConfig | None = None

# In-memory registry of live Drone objects keyed by their DB primary key.
# Populated during init_session() after drones are discovered and inserted.
_drones: dict[int, Drone] | None = None

# Flag indicating whether an AirSim session is active.
_is_running: bool = False


def is_running() -> bool:
    """Return True if the AirSim session is active, otherwise False.

    This is a lightweight guard for callers that need to verify the session
    lifecycle before issuing API calls that assume an initialized context.
    """
    global _is_running
    return _is_running


def init_session(airsim_config: AirSimConfig) -> None:
    """Initialize the global AirSim session with supplied configuration.

    Steps:
    1) Enforce single active session guard.
    2) Reset domain (orders/drones) to a clean state in the controller layer.
    3) Connect to AirSim and discover simulated drones.
    4) Initialize persistence (database) and register the drones.
    5) Build the in-memory drone registry keyed by DB IDs.

    :param airsim_config: Configuration for AirSim (IP, ports, etc.).
    :raises RuntimeError: If a session is already running.
    :raises ConnectionError: If client connection or discovery fails upstream.
    """
    global _airsim_config, _drones, _is_running

    if _is_running:
        # Defensive: prevent multiple concurrent sessions in the same process.
        msg = "AirSim session is already running."
        raise RuntimeError(msg)

    _airsim_config = airsim_config

    # Domain cleanup (controller layer). Removes leftover persisted state
    # so the new simulation session starts from a consistent baseline.
    from app.services.controller.drone_service import delete_drone, get_all_drones
    from app.services.controller.order_service import delete_order, get_all_orders

    for order in get_all_orders():
        delete_order(order.order_id)

    for drone in get_all_drones():
        delete_drone(drone.drone_id)

    # Establish AirSim client connection using provided host/port.
    # NOTE: Ensure the AirSim simulator is up and reachable before calling this.
    target_ip, target_port = (
        _airsim_config["LocalHostIp"],
        _airsim_config["ApiServerPort"],
    )

    # Query AirSim for available multirotor vehicles.
    # The returned list contains transient Drone wrappers (not DB rows yet).
    connect_client(target_ip, target_port)
    drones = create_drones_list()

    # Initialize database connection/tables if needed.
    init_db()

    # Build the in-memory registry as {db_id: Drone}
    _drones = {}

    # Persist each discovered drone and map its DB ID to the live Drone object.
    # Populate initial telemetry from AirSim state to seed the DB row.
    for drone in drones:
        drone.update_state()
        db_row = create_drone(
            drone_id=None,
            airsim_id=drone.vehicle_name,
            status=DroneStatus.IDLE,
            max_battery=10000,
            cur_battery=10000,
            max_payload=5,
            cur_payload=0,
            cur_lat=drone.state.gps_location.latitude,
            cur_lon=drone.state.gps_location.longitude,
            cur_alt=drone.state.gps_location.altitude,
        )
        # Link the live Drone wrapper to its persisted DB identity.
        drone.set_db_drone_id(db_row.drone_id)

        # Refresh live state after DB registration (optional, keeps code symmetric).
        drone.update_state()

        # Use the DB ID as the canonical key across layers.
        _drones[drone.id] = drone


def enqueue_order(order: Order) -> None:
    """Assign an order to an available drone and persist the assignment.

    Current policy:
    - Demonstration-only round-robin across all IDLE drones.
    - Calls sim_reset() and a short sleep to ensure a known baseline in sim.
      In production, prefer a targeted reset or a safer state transition.

    :param order: Order to be enqueued and dispatched.
    :raises ConnectionError: If no drones are discovered/registered.
    """
    global _drones
    if not _drones:
        msg = "No drones available in the AirSim simulation."
        raise ConnectionError(msg)

    # Reset the AirSim environment for a clean start (demo approach).
    sim_reset()
    time.sleep(3)

    # Force all tracked drones to IDLE before assignment (demo-only).
    for id, drone in _drones.items():
        drone._dstate = DroneStatus.IDLE

    # Filter to IDLE drones and choose one deterministically based on order ID.
    drones = [drone for id, drone in _drones.items() if drone.dstate == DroneStatus.IDLE]
    drone: Drone = drones[(order.order_id - 1) % len(drones)]  # Simple round-robin pickup

    # Dispatch the work to the chosen drone and persist the order record.
    drone.dispatch_order(order)
    create_order(order)


def get_order_status(id: int) -> Order | None:
    """Fetch the persisted order record by ID.

    This does not query the live simulator; it returns the DB-sourced view
    of the order. Use get_drone_progress for live telemetry + image bundle.

    :param id: Order ID (DB primary key).
    :return: Order object if present, otherwise None.
    """
    global _drones
    return get_order(id)


def get_drone_attr(id: int) -> MultirotorState | None:
    """Return the latest MultirotorState for a drone by DB ID.

    This performs a live update against the AirSim client for the given drone.
    If no such drone is registered in the in-memory registry, returns None.

    :param id: DB ID of the drone.
    :return: Up-to-date MultirotorState or None if not found.
    """
    drone = _drones.get(id, None)
    if not drone:
        return None

    return drone.update_state()


def end() -> None:
    """Terminate the AirSim session and disconnect the client.

    Marks the session as not running and closes the underlying client.
    Callers should re-run init_session() to start a new lifecycle.
    """
    global _is_running
    _is_running = False
    disconnect_client()


def get_drone_progress(order_id: int):
    """Return live progress for the drone handling the given order.

    If a drone is currently executing the order, returns the tuple produced by
    Drone.image_response(), which typically bundles:
      - data: telemetry dict (GPS, status, current order, etc.)
      - image: PNG bytes or {"image": (name, bytes, mime)}
    Otherwise returns None.

    :param order_id: Target order identifier to look up in active drones.
    :return: (data, image_payload) or None if no matching active order.
    """
    if not is_conneted():
        return None
    for drone in _drones.values():
        if drone.current_order and drone.current_order.order_id == order_id:
            # Delegate to Drone to package (data, image) for higher-level API.
            return drone.image_response()

    # No active drone found for this order ID (not assigned or already finished).
    return None
