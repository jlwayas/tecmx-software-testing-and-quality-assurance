"""
JSON file storage with basic validation and resilient error handling.

If invalid data exists, errors are printed and execution continues.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, TypeVar

T = TypeVar("T")


def _print_error(message: str) -> None:
    print(f"ERROR: {message}")


@dataclass
class JsonStore:
    """A simple JSON list store (list of dicts) for one entity type."""

    path: Path

    def load_raw_list(self) -> List[Dict[str, Any]]:
        """Load list of dicts from JSON file. If invalid, print error and return []."""
        if not self.path.exists():
            return []

        try:
            content = self.path.read_text(encoding="utf-8").strip()
            if not content:
                return []
            data = json.loads(content)
            if not isinstance(data, list):
                _print_error(f"{self.path.name}: root must be a JSON list")
                return []
            result: List[Dict[str, Any]] = []
            for idx, item in enumerate(data):
                if isinstance(item, dict):
                    result.append(item)
                else:
                    _print_error(
                        f"{self.path.name}: item at index {idx} is not an object"
                    )
            return result
        except (OSError, json.JSONDecodeError) as exc:
            _print_error(f"{self.path.name}: failed to read/parse JSON ({exc})")
            return []

    def save_raw_list(self, items: List[Dict[str, Any]]) -> None:
        """Save list of dicts to JSON file."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(items, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError as exc:
            _print_error(f"{self.path.name}: failed to write JSON ({exc})")

    def load_items(self, parser: Callable[[Dict[str, Any]], T]) -> List[T]:
        """
        Load and parse items. Invalid entries are skipped with an error message.
        """
        raw_list = self.load_raw_list()
        parsed: List[T] = []
        for idx, raw in enumerate(raw_list):
            try:
                parsed.append(parser(raw))
            except (KeyError, TypeError, ValueError) as exc:
                _print_error(f"{self.path.name}: invalid item at index {idx} ({exc})")
        return parsed
