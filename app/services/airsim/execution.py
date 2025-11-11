"""TODO: Launch AirSim simulation with specified configurations."""

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
    sim_reset,
)

from .config import AirSimConfig

_airsim_config: AirSimConfig | None = None
_drones: dict[int, Drone] | None = None
_is_running: bool = False


def is_running() -> bool:
    """Check if the AirSim session is running."""
    global _is_running
    return _is_running


def init_session(airsim_config: AirSimConfig) -> None:
    """Initialize the global session with AirSim configuration.

    :param airsim_config: Configuration for AirSim.
    """
    global _airsim_config, _drones, _is_running

    if _is_running:
        msg = "AirSim session is already running."
        raise RuntimeError(msg)

    _airsim_config = airsim_config

    from app.services.controller.drone_service import delete_drone, get_all_drones
    from app.services.controller.order_service import delete_order, get_all_orders

    for order in get_all_orders():
        delete_order(order.order_id)

    for drone in get_all_drones():
        delete_drone(drone.drone_id)

    # Set up AirSim client
    target_ip, target_port = (
        _airsim_config["LocalHostIp"],
        _airsim_config["ApiServerPort"],
    )

    connect_client(target_ip, target_port)
    drones = create_drones_list()

    # Set up drone database
    init_db()
    _drones = {}

    # Create drones in the database
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
        drone.set_db_drone_id(db_row.drone_id)
        drone.update_state()
        _drones[drone.id] = drone


def enqueue_order(order: Order) -> None:
    """Enqueue an order to a drone.

    :param order: Order to be enqueued.
    """
    global _drones
    if not _drones:
        msg = "No drones available in the AirSim simulation."
        raise ConnectionError(msg)

    # Simple round-robin assignment for demonstration purposes
    sim_reset()
    time.sleep(3)
    for id, drone in _drones.items():
        drone._dstate = DroneStatus.IDLE
    drones = [drone for id, drone in _drones.items() if drone.dstate == DroneStatus.IDLE]
    drone: Drone = drones[(order.order_id - 1) % len(drones)]  # 뽑기 로직
    drone.dispatch_order(order)
    create_order(order)


def get_order_status(id: int) -> Order | None:
    """Get the status of an order by its ID.

    :param id: ID of the order.
    :return: The order object if found, otherwise None.
    """
    global _drones
    return get_order(id)


def get_drone_attr(id: int) -> MultirotorState | None:
    """Get the current attributes of a drone by its ID.

    :param id: ID of the drone.
    :return: The current state of the drone or None if not found.
    """
    drone = _drones.get(id, None)
    if not drone:
        return None

    return drone.update_state()


def end() -> None:
    """End the simulation session."""
    global _is_running
    _is_running = False
    disconnect_client()


def get_drone_progress(order_id: int):
    for drone in _drones.values():
        if drone.current_order and drone.current_order.order_id == order_id:
            return drone.image_response()

    return None
