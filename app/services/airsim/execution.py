"""TODO: Launch AirSim simulation with specified configurations."""

from app.configs import Config
from app.models.drone import DroneStatus
from app.services.controller.database import drop_all_tables, init_db
from app.services.controller.drone_service import create_drone
from app.utils.airsimutils import (
    Drone,
    connect_client,
    create_drones_list,
    disconnect_client,
)
from models.order import Order

from .config import AirSimConfig


class SimulationSession(Config):
    """Class to manage a simulation session with AirSim."""

    _airsim_config: AirSimConfig
    _drones: list[Drone]

    def __init__(
        self,
        airsim_config: AirSimConfig,
    ) -> None:
        """Initialize the simulation session with AirSim and drone group configurations.

        :param airsim_config: Configuration for AirSim.
        :param drone_group_config: Configuration for the drone group.
        """
        self._drones = []

        # Set up AirSim client
        self._airsim_config = airsim_config
        target_ip = self._airsim_config["LocalHostIp"]
        target_port = self._airsim_config["ApiServerPort"]

        connect_client(target_ip, target_port)
        self._drones = create_drones_list()

        # Set up drone database
        init_db()
        drop_all_tables()

        # Create drones in the database
        for drone in self._drones:
            create_drone(
                drone_id=drone.id,
                status=DroneStatus.IDLE,
                max_battery=10000,
                cur_battery=10000,
                max_payload=5,
                cur_payload=0,
                cur_lat=drone.state.gps_location.latitude,
                cur_lon=drone.state.gps_location.longitude,
                cur_alt=drone.state.gps_location.altitude,
            )

    def enqueue_order(self, order: Order) -> None:
        """Enqueue an order to a drone.

        :param order: Order to be enqueued.
        """
        if not self._drones:
            msg = "No drones available in the AirSim simulation."
            raise ConnectionError(msg)
        # Simple round-robin assignment for demonstration purposes
        drone: Drone = self._drones[order.order_id % len(self._drones)]
        drone.dispatch_order(order)

    def end(self) -> None:
        """End the simulation session."""
        disconnect_client()
