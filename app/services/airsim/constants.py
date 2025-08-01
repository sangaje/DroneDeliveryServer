"""app/services/airsim/constants.py - Constants for AirSim configurations."""

from pathlib import Path

DEFAULT_CONFIGS_PATH = str(Path.home() / "ddaip/airsim/")
AIRSIM_CONFIG_DEFAULT_PATH = str(Path(DEFAULT_CONFIGS_PATH) / "airsim_configs.json")

AIRSIM_CONFIG_KEY = "AirsimConfigs"
CUSTUM_AIRSIM_CONFIG_KEY = "CustomAirsimConfigs"
DEFAULT_AIRSIM_CONFIG_KEY = "DefaultSettings"

DRONE_GROUP_KEY = "DroneGroups"
DEFAULT_DRONE_GROUP = "DefaultDroneGroup"
DEFAULT_DORNE_GROUP_PATH = "app/configs/default_drone_group.json"

DEFAULT_SETTINGS_PATH = "app/configs/default_settings.json"
