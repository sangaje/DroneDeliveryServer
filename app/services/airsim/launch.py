"""TODO: Launch AirSim simulation with specified configurations."""

from app.configs import Config
from app.services.controller.database import drop_all_tables, init_db
from app.services.controller.drone_service import create_drone
from app.utils.airsimutils import Drone, connect_client, create_drones_list, disconnect_client

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
            # TODO: change to use drone.id when constructor is fixed
            _ = drone
            create_drone()

    def end(self) -> None:
        """End the simulation session."""
        disconnect_client()
