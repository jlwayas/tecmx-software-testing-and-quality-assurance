import tempfile
import unittest
from pathlib import Path

from reservation_system.services import build_services


class TestInvalidDataHandling(unittest.TestCase):
    def test_invalid_json_does_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            (data_dir / "hotels.json").write_text("{ invalid json", encoding="utf-8")

            services = build_services(data_dir)
            hotels = services["hotels"]

            self.assertEqual(hotels.list_hotels(), [])

    def test_wrong_root_type_is_handled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            (data_dir / "customers.json").write_text('"not a list"', encoding="utf-8")

            services = build_services(data_dir)
            customers = services["customers"]

            self.assertEqual(customers.list_customers(), [])