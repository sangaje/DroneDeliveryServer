"""jsonutils.py - utiulities for handling JSON files and dictionaries.

This module provides functions to load, save, validate, and manipulate JSON data.

Functions:
- load_json: Load a JSON file and return its content as a dictionary.
- save_json: Save a dictionary to a JSON file.
"""

import json
from pathlib import Path


class InvalidJSONLoadArgumentsError(ValueError):
    """Exception raised when neither path nor data is provided to load JSON data."""

    def __init__(self) -> None:
        """Exception raised when neither path nor data is provided to load JSON data."""
        super().__init__("Either 'path' or 'data' must be provided to load JSON data.")


def load_json(path: str | Path | None = None, data: bytes | str | None = None) -> dict:
    """Load a JSON file and return its content as a dictionary.

    :param path: Path to the JSON file.
    :return: Parsed JSON data as a dictionary.
    :raises json.JSONDecodeError: If the file content is not valid JSON.
    :raises ValueError: If neither path nor data is provided.
    :raises FileNotFoundError: If the specified path does not exist.
    """
    if data is not None:
        return json.loads(data)

    if path is not None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    raise InvalidJSONLoadArgumentsError


def save_json(path: str | Path, data: dict, indent: int = 4, ensure_ascii: bool = False) -> None:
    """Save a dictionary to a JSON file.

    :param path: Path to the JSON file.
    :param data: Data to save in the JSON file.
    :param indent: Indentation level for pretty printing.
    :param ensure_ascii: If True, non-ASCII characters are escaped.
    :raise FileNotFoundError: If the specified path does not exist.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
