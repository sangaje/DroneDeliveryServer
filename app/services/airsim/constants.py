"""app/services/airsim/constants.py - Constants for AirSim configurations."""

from pathlib import Path

DEFAULT_CONFIGS_PATH = str(Path.home() / "ddaip/airsim/")  # Default path for AirSim configurations
AIRSIM_CONFIG_DEFAULT_PATH = str(
    Path(DEFAULT_CONFIGS_PATH) / "airsim_configs.json"
)  # Default path for AirSim configurations file

AIRSIM_CONFIG_KEY = "AirsimConfigs"  # Key for AirSim configurations
CUSTOM_AIRSIM_CONFIG_KEY = "CustomAirsimConfigs"  # Key for custom AirSim configurations
DEFAULT_AIRSIM_CONFIG_KEY = "DefaultSettings"  # Key for default AirSim settings

DRONE_GROUP_KEY = "DroneGroups"  # Key for drone group configurations
DEFAULT_DRONE_GROUP = "DefaultDroneGroup"  # Default drone group name
DEFAULT_DRONE_GROUP_PATH = (
    "app/configs/default_drone_group.json"  # Default path for drone group configurations
)

DEFAULT_SETTINGS_PATH = "app/configs/default_settings.json"  # Default path for AirSim settings
