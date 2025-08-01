"""tests/utils/test_load_json.py - Unit tests for JSON utilities.

This module contains unit tests for the JSON utilities provided in app/utils/jsonutils.py.
"""

import json
from pathlib import Path

from app.utils.jsonutils import InvalidJSONLoadArgumentsError, load_json
import pytest


def test_load_json_from_string() -> None:
    """Test loading JSON data from a string."""
    data = '{"a": 1, "b": 2}'
    result = load_json(data=data)
    assert result == {"a": 1, "b": 2}


def test_load_json_from_bytes() -> None:
    """Test loading JSON data from bytes."""
    data = b'{"x": 10, "y": 20}'
    result = load_json(data=data)
    assert result == {"x": 10, "y": 20}


def test_load_json_invalid_string() -> None:
    """Test loading invalid JSON string raises JSONDecodeError."""
    with pytest.raises(json.JSONDecodeError):
        load_json(data='{"invalid": }')


def test_load_json_invalid_bytes() -> None:
    """Test loading invalid JSON bytes raises JSONDecodeError."""
    with pytest.raises(json.JSONDecodeError):
        load_json(data=b'{"invalid": }')


def test_load_json_from_valid_file(tmp_path: Path) -> None:
    """Test loading JSON data from a valid file path."""
    path = tmp_path / "valid.json"
    path.write_text('{"foo": "bar"}', encoding="utf-8")
    result = load_json(path=path)
    assert result == {"foo": "bar"}


def test_load_json_from_invalid_json_file(tmp_path: Path) -> None:
    """Test loading invalid JSON content from file raises JSONDecodeError."""
    path = tmp_path / "invalid.json"
    path.write_text("{ invalid json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_json(path=path)


def test_load_json_file_not_found(tmp_path: Path) -> None:
    """Test loading from non-existent file path raises FileNotFoundError."""
    path = tmp_path / "nonexistent.json"
    with pytest.raises(FileNotFoundError):
        load_json(path=path)


def test_load_json_without_arguments() -> None:
    """Test that calling load_json with neither path nor data raises ValueError."""
    with pytest.raises(InvalidJSONLoadArgumentsError):
        load_json()
