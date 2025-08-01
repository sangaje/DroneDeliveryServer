"""tests/utils/test_save_json.py - Unit tests for JSON utilities.

This module contains unit tests for the JSON utilities provided in app/utils/jsonutils.py.
"""

import json
from pathlib import Path

from app.utils.jsonutils import save_json
import pytest


def test_save_json_basic(tmp_path: Path) -> None:
    """Test saving a basic dictionary to a JSON file."""
    file_path = tmp_path / "basic.json"
    data = {"x": 1, "y": "test"}
    save_json(file_path, data)

    # Check that file exists
    assert file_path.exists()

    # Check that contents match original data
    content = json.loads(file_path.read_text(encoding="utf-8"))
    assert content == data


def test_save_json_unicode_characters(tmp_path: Path) -> None:
    """Test saving non-ASCII characters with ensure_ascii=False."""
    file_path = tmp_path / "unicode.json"
    data = {"message": "안녕하세요"}
    save_json(file_path, data, ensure_ascii=False)

    # Ensure the actual string appears in the file (not escaped)
    text = file_path.read_text(encoding="utf-8")
    assert "안녕하세요" in text


def test_save_json_ascii_escaped(tmp_path: Path) -> None:
    """Test saving non-ASCII characters with ensure_ascii=True."""
    file_path = tmp_path / "ascii.json"
    data = {"message": "안녕하세요"}
    save_json(file_path, data, ensure_ascii=True)

    # Ensure unicode is escaped
    text = file_path.read_text(encoding="utf-8")
    assert "\\u" in text


def test_save_json_to_nonexistent_directory(tmp_path: Path) -> None:
    """Test saving to a file inside a non-existent directory raises FileNotFoundError."""
    invalid_path = tmp_path / "nonexistent_dir" / "file.json"
    data = {"fail": True}

    # Expect failure due to missing parent directory
    with pytest.raises(FileNotFoundError):
        save_json(invalid_path, data)
