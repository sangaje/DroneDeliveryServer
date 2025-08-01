"""app/configs/config.py - Configuration utilities for the Drone Delivery Server application."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from app.utils.jsonutils import load_json, save_json

from .constants import APP_CONFIG_PATH


class InvalidSearchArgumentsError(ValueError):
    """Exception raised when invalid arguments are provided to search for a key in a dictionary."""

    def __init__(self, data: dict, key: str) -> None:
        """Initialize the exception with a message indicating the invalid arguments."""
        super().__init__(f"Invalid search arguments: {data}, {key}")


class InvalidSetKeyArgumentsError(ValueError):
    """Exception raised when invalid arguments are provided to set a key in a dictionary."""

    def __init__(self, data: dict, key: str | None) -> None:
        """Initialize the exception with a message indicating the invalid arguments."""
        super().__init__(f"Invalid set key arguments: {data}, {key}")


class Config:
    """Configuration class for managing application settings."""

    _data: dict[str, Any]
    _file: str | Path | None

    def __init__(
        self, data: dict | bytes | str | None = None, config_file_path: str | Path | None = None
    ) -> None:
        """Initialize the Config object with data or a JSON file path.

        :param data: Optional dictionary to initialize the configuration.
        :param config_file_path: Optional path to a JSON file to load the configuration from.
        """
        if config_file_path:
            self._data = load_json(path=config_file_path)
            self._file = config_file_path
            return

        self._file = None
        if isinstance(data, bytes | str):
            self._data = load_json(data=data)
            return

        if isinstance(data, dict):
            self._data = data
            return

        self._data = {}

    @classmethod
    def from_dict(cls, data: dict) -> Config:
        """Create a Config instance from a dictionary.

        :param data: Dictionary containing configuration data.
        :return: Config instance initialized with the provided dictionary.
        """
        return cls(data)

    @classmethod
    def from_file(cls, config_file_path: str | Path) -> Config:
        """Create a Config instance from a JSON file.

        :param config_file_path: Path to the JSON file containing configuration data.
        :return: Config instance initialized with the data from the file.
        """
        return cls(config_file_path=config_file_path)

    @classmethod
    def from_binary(cls, data: bytes) -> Config:
        """Create a Config instance from binary data.

        :param data: Binary data containing JSON configuration.
        :return: Config instance initialized with the binary data.
        """
        return cls(data=data)

    def to_dict(self) -> dict:
        """Convert the configuration data to a dictionary."""
        return deepcopy(self._data)

    def __getitem__(self, key: str | list | tuple) -> Any:
        """Get a value from the configuration.

        :param key: The key to retrieve, can be a dot-separated string or a list of keys.
        :return: The value associated with the key.
        """
        return self.get(key)

    @staticmethod
    def _parse_key(key: str | list[str] | tuple[str, ...]) -> list[str]:
        """Parse the key into a list of strings.

        :param key: The key to parse, can be a dot-separated string or a list of keys.
        :return: List of keys.
        :raises TypeError: If the key is not a string, list, or tuple.
        """
        if isinstance(key, str):
            return key.split(".")
        if isinstance(key, list | tuple):
            if not all(isinstance(k, str) for k in key):
                raise TypeError(type(key))
            return list(key)
        raise TypeError(type(key).__name__)

    def __setitem__(self, key: str | list | tuple, value: Any) -> None:
        """Set a value in the configuration.

        :param key: The key to set, can be a dot-separated string or a list of keys.
        :param value: The value to set.
        """
        keys = self._parse_key(key)

        if self._data is None:
            self._data = {}

        node = self._data
        for k in keys[:-1]:
            if k not in node or not isinstance(node[k], dict):
                node[k] = {}
            node = node[k]

        node[keys[-1]] = value

        if self._file is not None:
            self.save()

    def save(self, path: str | Path | None = None) -> None:
        """Save the configuration to a file.

        :param path: Optional path to save the configuration file. If None, uses the existing file
            path.
        """
        if path is not None:
            self._file = path

        if self._file is None:
            raise ValueError(type(self._file), self._file)

        save_json(data=self._data, path=self._file)

    def set_path(self, path: str | Path) -> None:
        """Set the path for the configuration file.

        :param path: Path to the configuration file.
        """
        self._file = str(path)

    def get(self, key: str | list | tuple, default: Any = None) -> Any:
        """Get a value from the configuration.

        :param key: The key to retrieve, can be a dot-separated string or a list of keys.
        :param default: Default value to return if the key is not found.
        :return: The value associated with the key, or default if not found.
        """
        keys = self._parse_key(key)

        if self._data is None:
            self._data = {}

        node = self._data
        for k in keys:
            if isinstance(node, dict) and k in node:
                node = node[k]
            else:
                return default

        return node

    def __repr__(self) -> str:
        """Return a string representation of the Config object."""
        return f"<Config keys={list(self._data.keys())!s}>"


class AppConfig(Config):
    """Application configuration class that extends the base Config class."""

    _instance: AppConfig | None = None

    def __new__(cls) -> AppConfig:
        """Ensure only one instance of AppConfig is created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the AppConfig instance."""
        if not hasattr(self, "_initialized"):
            super().__init__(config_file_path=APP_CONFIG_PATH)
            self._initialized = True

    @classmethod
    def load(cls) -> AppConfig:
        """Load the application configuration."""
        return cls()
