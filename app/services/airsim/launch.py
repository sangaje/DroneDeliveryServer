"""TODO: Launch AirSim simulation with specified configurations."""

from time import time

from app.configs import Config

from .config import AirSimConfig, DroneGroupConfig


class SimulationSession(Config):
    """Class to manage a simulation session with AirSim."""

    _airsim_config: AirSimConfig
    _drone_group_config: list[DroneGroupConfig]

    def __init__(
        self,
        airsim_config: AirSimConfig,
        drone_group_config: DroneGroupConfig | list[DroneGroupConfig],
    ):
        """Initialize the simulation session with AirSim and drone group configurations.

        :param airsim_config: Configuration for AirSim.
        :param drone_group_config: Configuration for the drone group.
        """
        self.airsim_config = airsim_config

        if isinstance(drone_group_config, DroneGroupConfig):
            drone_group_config = [drone_group_config]
        else:
            self.drone_group_config = drone_group_config
        self._session_id = hash(time())

    # def launch(self) -> Any:
    #     """Launch the AirSim simulation with the specified configurations."""
    #     settings = AirSimSettings(self.airsim_config, self.drone_group_config)
    #     return settings.launch_simulation()
