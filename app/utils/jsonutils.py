"""
jsonutils.py - utiulities for handling JSON files and dictionaries.

This module provides functions to load, save, validate, and manipulate JSON data.

Functions:
- load_json: Load a JSON file and return its content as a dictionary.
- save_json: Save a dictionary to a JSON file.
"""

from pathlib import Path
import json
from collections.abc import MutableMapping
from typing import Any, Union


def load_json(path: Union[str, Path]) -> dict:
    """
    Load a JSON file and return its content as a dictionary.
    :param path: Path to the JSON file.
    :return: Parsed JSON data as a dictionary.
    :raises FileNotFoundError: If the JSON file does not exist.
    :raises json.JSONDecodeError: If the file content is not valid JSON.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(
    path: Union[str, Path], data: dict, indent: int = 4, ensure_ascii: bool = False
):
    """
    Save a dictionary to a JSON file.
    :param path: Path to the JSON file.
    :param data: Data to save in the JSON file.
    :param indent: Indentation level for pretty printing.
    :param ensure_ascii: If True, non-ASCII characters are escaped.
    """
    path = Path(path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)