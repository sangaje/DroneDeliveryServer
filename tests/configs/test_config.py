"""tests/configs/test_config.py - Unit tests for configuration loading utilities."""

import json
from pathlib import Path
from typing import Any

from app.configs import Config
import pytest


@pytest.fixture
def sample_dict() -> dict[str, Any]:
    """Return a nested sample configuration dictionary."""
    return {
        "sim_mode": "Multirotor",
        "settings": {
            "camera": {"resolution": {"width": 1920, "height": 1080}, "fov": 120},
            "weather": {"enable": True, "wind": {"speed": 15, "direction": "NE"}},
        },
        "metadata": {"author": "bo_min", "version": 1.2, "tags": ["drone", "airsim", "config"]},
    }


def test_from_dict_and_get_set(sample_dict: dict) -> None:
    """Test creation from dict and deep key get/set functionality."""
    cfg = Config.from_dict(sample_dict)

    assert cfg["sim_mode"] == "Multirotor"
    assert cfg["settings.camera.resolution.width"] == 1920
    assert cfg["settings.weather.wind.direction"] == "NE"
    assert cfg.get("metadata.version") == 1.2
    assert cfg.get("nonexistent", default="default") == "default"

    # Test __getitem__ fallback to get
    assert cfg["metadata.tags"] == ["drone", "airsim", "config"]

    # Test deep __setitem__
    cfg["settings.camera.resolution.height"] = 720
    assert cfg["settings.camera.resolution.height"] == 720

    cfg["settings.weather.humidity"] = 50
    assert cfg["settings.weather.humidity"] == 50

    # Test nested set for non-existing path
    cfg["new.path.created"] = "yes"
    assert cfg["new.path.created"] == "yes"


def test_from_json_string_and_binary(sample_dict: dict) -> None:
    """Test creation from JSON string and binary."""
    json_str = json.dumps(sample_dict)
    json_bytes = json_str.encode("utf-8")

    cfg_from_str = Config(data=json_str)
    cfg_from_bytes = Config(data=json_bytes)

    assert cfg_from_str["sim_mode"] == "Multirotor"
    assert cfg_from_bytes["settings.camera.fov"] == 120


def test_from_file(tmp_path: Path, sample_dict: dict) -> None:
    """Test loading configuration from a JSON file."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(sample_dict), encoding="utf-8")

    cfg = Config.from_file(config_path)
    assert cfg["metadata.author"] == "bo_min"
    assert cfg["settings.weather.enable"] is True


def test_to_dict_isolated(sample_dict: dict) -> None:
    """Ensure to_dict returns a deep copy."""
    cfg = Config.from_dict(sample_dict)
    original = cfg.to_dict()

    original["settings"]["camera"]["resolution"]["width"] = 100  # Mutate
    # Re-fetch from cfg to ensure immutability
    assert cfg["settings.camera.resolution.width"] == 1920


def test_repr(sample_dict: dict) -> None:
    """Test __repr__ gives meaningful representation."""
    cfg = Config.from_dict(sample_dict)
    repr_str = repr(cfg)
    assert repr_str.startswith("<Config keys=")
    assert "sim_mode" in repr_str
    assert isinstance(repr_str, str)


def test_missing_key_returns_default() -> None:
    """Check default return for missing keys."""
    cfg = Config.from_dict({})
    assert cfg.get("nonexistent.key") is None
    assert cfg.get("nonexistent.key", default=123) == 123


def test_dot_and_list_key_equivalence(sample_dict: dict) -> None:
    """Ensure that dot-separated and list keys behave identically."""
    cfg = Config.from_dict(sample_dict)

    key_dot = "settings.camera.resolution.width"
    key_list = ["settings", "camera", "resolution", "width"]

    assert cfg.get(key_dot) == cfg.get(key_list)
    assert cfg[key_dot] == cfg[key_list]

    # Set both ways
    cfg[key_list] = 999
    assert cfg[key_dot] == 999


def test_nested_set_and_get_with_empty_dict() -> None:
    """Test setting deep values into initially empty config."""
    cfg = Config()

    cfg["a.b.c.d"] = 42
    assert cfg["a.b.c.d"] == 42
    assert cfg.get("a.b.c") == {"d": 42}


def test_set_path_and_save_json(tmp_path: Path) -> None:
    """Test that `set_path()` correctly updates the internal file path, and `save()'."""
    # Given: Initial config data
    config_data = {"mission": {"name": "drone_test", "speed": 15}}
    config = Config.from_dict(config_data)

    # When: Path is set manually via set_path()
    target_path = tmp_path / "test_config.json"
    config.set_path(target_path)
    config.save()

    # Then: File should exist and contain the correct data
    assert target_path.exists(), "Saved file does not exist"

    import json

    with open(target_path, encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data == config_data, "Saved data does not match original config"


def test_save_with_path_argument(tmp_path: Path) -> None:
    """Test that providing a path to `save()` correctly updates and saves to that file."""
    config_data = {"settings": {"camera": {"fov": 90}}}
    config = Config.from_dict(config_data)

    save_path = tmp_path / "settings_config.json"
    config.save(save_path)

    assert save_path.exists(), "Config file was not created with provided path"

    import json

    with open(save_path, encoding="utf-8") as f:
        saved = json.load(f)

    assert saved == config_data, "Saved data does not match original"
