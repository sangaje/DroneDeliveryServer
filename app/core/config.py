"""config.py - Configuration management for the application.

This module provides functions to load and save JSON configuration files.
Functions:
- load_config: Load a JSON configuration file and return its content as a dictionary.
- save_config: Save a dictionary to a JSON configuration file.
"""

from enum import Enum
from pathlib import Path

DEFAULT_CONFIG_DIR = Path("app/configs")  # Default directory for configuration files
APP_CONFIG_FILE = Path("app/configs/application_config.json")  # application configuration file


class ConfigFile(str, Enum):
    """Enum for configuration file names.

    This allows for easy reference to configuration files in the application.
    """

    APPLICATION_CONFIG = 0
    AIRSIM_SETTINGS = 1
    SIMULATION_SETTINGS = 2


# TODO: Implement a function to load the configuration file based on the enum value
# def load_config(config: ConfigFile) -> dict:
#     """Load a JSON configuration file.

#     :param filename: Name of the configuration file.
#     :return: Parsed JSON data as a dictionary.
#     :raises FileNotFoundError: If the configuration file does not exist.
#     """
#     if not path.exists():
#         raise FileNotFoundError(f"{path} does not exist.")
#     with path.open("r", encoding="utf-8") as f:
#         return json.load(f)


# def save_config(config: ConfigFile, data: dict):
#     """Save a dictionary to a JSON configuration file.

#     :param filename: Name of the configuration file.
#     :param data: Data to save in the configuration file.
#     """
#     path = CONFIG_DIR / filename
#     with path.open("w", encoding="utf-8") as f:
#         json.dump(data, f, indent=4, ensure_ascii=False)
