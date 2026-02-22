"""Unit tests for invalid JSON / invalid structure handling."""

import tempfile
import unittest
from pathlib import Path

from reservation_system.services import build_services


class TestInvalidDataHandling(unittest.TestCase):
    """Tests that invalid persisted data does not crash the system."""

    def test_invalid_json_does_not_crash(self) -> None:
        """Corrupted JSON should be handled and return empty results."""
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            (data_dir / "hotels.json").write_text("{ invalid json", encoding="utf-8")

            services = build_services(data_dir)
            hotels = services["hotels"]

            self.assertEqual(hotels.list_hotels(), [])

    def test_wrong_root_type_is_handled(self) -> None:
        """Non-list JSON root should be handled and return empty results."""
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            (data_dir / "customers.json").write_text('"not a list"', encoding="utf-8")

            services = build_services(data_dir)
            customers = services["customers"]

            self.assertEqual(customers.list_customers(), [])
