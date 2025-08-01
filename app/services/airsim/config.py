"""config.py - Configuration utilities for AirSim integration in the Drone Delivery Server.

This module provides functions to load and manage AirSim-specific configurations.
"""

from __future__ import annotations

from pathlib import Path

from app.configs import (
    AppConfig,
    Config,
)

from .constants import (
    AIRSIM_CONFIG_DEFAULT_PATH,
    AIRSIM_CONFIG_KEY,
    CUSTOM_AIRSIM_CONFIG_KEY,
    DEFAULT_AIRSIM_CONFIG_KEY,
    DEFAULT_CONFIGS_PATH,
    DEFAULT_DRONE_GROUP,
    DEFAULT_DRONE_GROUP_PATH,
    DEFAULT_SETTINGS_PATH,
    DRONE_GROUP_KEY,
)


class AirSimConfig(Config):
    """Class to handle AirSim-specific configurations."""

    _instance: AirSimConfig | None = None

    def __new__(cls) -> AirSimConfig:
        """Ensure only one instance of AppConfig is created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the AppConfig instance."""
        if not hasattr(self, "_initialized"):
            app_config = AppConfig()
            self._file = app_config[AIRSIM_CONFIG_KEY]
            if not self._file:
                super().__init__()
                self.set_path(AIRSIM_CONFIG_DEFAULT_PATH)
                self[DEFAULT_AIRSIM_CONFIG_KEY] = DEFAULT_SETTINGS_PATH
                self[DEFAULT_DRONE_GROUP] = DEFAULT_DRONE_GROUP_PATH
                self.save()

                app_config[AIRSIM_CONFIG_KEY] = self._file
                app_config.save()

            else:
                try:
                    super().__init__(config_file_path=self._file)
                except FileNotFoundError:
                    # If the file does not exist, create a new one with default settings
                    super().__init__()
                    self.set_path(AIRSIM_CONFIG_DEFAULT_PATH)
                    self[DEFAULT_AIRSIM_CONFIG_KEY] = DEFAULT_SETTINGS_PATH
                    self[DEFAULT_DRONE_GROUP] = DEFAULT_DRONE_GROUP_PATH
                    self.save()

                    app_config[AIRSIM_CONFIG_KEY] = self._file
                    app_config.save()
            self._initialized = True

    def config_names(self, config_key: str = "") -> list[str]:
        """Generate an HTML select form for AirSim configurations."""
        if self[config_key] is None:
            return []
        return self[config_key].keys()


class _BaseAirSimConfig(Config):
    """Base class for AirSim configurations."""

    _name: str

    def __init__(
        self,
        config_name: str = "",
        default_key: str = "",
        custum_key: str = "",
    ) -> None:
        """Initialize the base AirSim configuration.

        :param config_name: Name of the AirSim configuration to load. If empty, uses the default
            configuration.
        :param DEFAULT_KEY: Key for the default AirSim configuration.
        :param CUSTUM_KEY: Key for custom AirSim configurations.
        :param DEFAULT_PATH: Path to the default AirSim configuration file.
        """
        airsim_config = AirSimConfig()
        self._CUSTUM_KEY = custum_key

        if not config_name:
            settings = airsim_config[default_key]
            self._name = ""
        else:
            settings = airsim_config[custum_key, config_name]
            self.name = config_name

        if settings:
            super().__init__(config_file_path=settings)
            self.save()

        # If the custom configuration does not exist, create a new one
        else:
            settings = airsim_config[default_key]
            super().__init__(config_file_path=settings)
            self.name = config_name
            self.save()

            airsim_config[custum_key, config_name] = self._file
            airsim_config.save()

    def set_path(self, file_name: str | Path) -> None:
        """Set the path for the AirSim configuration file.

        :param file_name: Name of the AirSim configuration file.
        """
        file_path = Path(DEFAULT_CONFIGS_PATH) / self._CUSTUM_KEY / Path(f"{file_name}.json")
        self._name = str(file_name)
        return super().set_path(file_path)

    def save(self, file_name: str | Path | None = None) -> None:
        """Save the AirSim configuration to a file.

        :param path: Optional path to save the configuration file. If None, uses the existing file
            path.
        """
        if file_name is not None:
            self.set_path(file_name)

        if not self._name:
            return

        super().save()

        airsim_config = AirSimConfig()
        airsim_config[self._CUSTUM_KEY, self._name] = self._file
        airsim_config.save()

    @property
    def name(self) -> str:
        """Get the name of the AirSim configuration."""
        return self._name

    @name.setter
    def name(self, value: str | Path) -> None:
        """Set the name of the AirSim configuration."""
        self.set_path(str(value))

    @property
    def html_form(self) -> str:
        """Generate an HTML form for the AirSim configuration."""
        return render_form(self._data, readonly=False)


class AirSimSettings(_BaseAirSimConfig):
    """Class to handle AirSim settings configurations."""

    def __init__(self, config_name: str = "") -> None:
        """Initialize the AirSimSettings instance.

        :param config_name: Name of the AirSim configuration to load. If empty, uses the default
            configuration.
        """
        super().__init__(
            config_name=config_name,
            default_key=DEFAULT_AIRSIM_CONFIG_KEY,
            custum_key=CUSTOM_AIRSIM_CONFIG_KEY,
        )
        self["SimMode"] = "Multirotor"


class DroneGroupConfig(_BaseAirSimConfig):
    """Class to handle Drone Group configurations."""

    def __init__(self, config_name: str = "") -> None:
        """Initialize the DroneGroupConfig instance.

        :param config_name: Name of the Drone Group configuration to load.
        """
        super().__init__(
            config_name=config_name,
            default_key=DEFAULT_DRONE_GROUP,
            custum_key=DRONE_GROUP_KEY,
        )


def render_form(data: dict, prefix: str = "", readonly: bool = False) -> str:
    """Render a form from a dictionary.

    :param data: Dictionary containing form data.
    :param prefix: Prefix for form field names.
    :return: HTML string representing the form.
    :raises ValueError: If data is not a dictionary.
    """
    html = ""
    postfix = "readonly" if readonly else ""
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            html += f"<fieldset><legend>{key}</legend>"
            html += render_form(value, prefix=full_key)
            html += "</fieldset>"
        else:
            if isinstance(value, bool):
                input_html = (
                    f'<input type="checkbox" id="{full_key}" name="{full_key}" value="true"'
                    + (" checked" if value else "")
                    + f" {postfix} >"
                )
            elif isinstance(value, int):
                input_html = (
                    f'<input type="number" step="1" id="{full_key}" name="{full_key}"'
                    f' value="{value}" {postfix}>'
                )
            elif isinstance(value, float):
                input_html = (
                    f'<input type="number" step="any" id="{full_key}" name="{full_key}"'
                    f' value="{value}" {postfix}>'
                )
            else:
                input_html = (
                    f'<input type="text" id="{full_key}" name="{full_key}"'
                    f' value="{value}" {postfix}>'
                )

            html += f'<label for="{full_key}">{key}</label>'
            html += input_html
    return html
