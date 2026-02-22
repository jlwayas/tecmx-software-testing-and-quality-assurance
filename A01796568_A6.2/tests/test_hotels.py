import tempfile
import unittest
from pathlib import Path

from reservation_system.models import Hotel
from reservation_system.services import ValidationError, build_services


class TestHotelService(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp.name)
        services = build_services(self.data_dir)
        self.hotels = services["hotels"]

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_create_and_get_hotel(self) -> None:
        hotel = Hotel("H1", "Ritz", "CDMX", 10, 10)
        self.hotels.create_hotel(hotel)
        loaded = self.hotels.get_hotel("H1")
        self.assertEqual(loaded.name, "Ritz")

    def test_modify_hotel(self) -> None:
        self.hotels.create_hotel(Hotel("H1", "Ritz", "CDMX", 10, 10))
        self.hotels.modify_hotel("H1", name="Ritz Updated", available_rooms=9)
        loaded = self.hotels.get_hotel("H1")
        self.assertEqual(loaded.name, "Ritz Updated")
        self.assertEqual(loaded.available_rooms, 9)

    def test_reserve_rooms_success(self) -> None:
        self.hotels.create_hotel(Hotel("H1", "Ritz", "CDMX", 10, 10))
        self.hotels.reserve_rooms("H1", 3)
        loaded = self.hotels.get_hotel("H1")
        self.assertEqual(loaded.available_rooms, 7)

    def test_reserve_rooms_not_enough(self) -> None:
        self.hotels.create_hotel(Hotel("H1", "Ritz", "CDMX", 2, 2))
        with self.assertRaises(ValidationError):
            self.hotels.reserve_rooms("H1", 3)

    def test_release_rooms_success(self) -> None:
        self.hotels.create_hotel(Hotel("H1", "Ritz", "CDMX", 10, 5))
        self.hotels.release_rooms("H1", 2)
        loaded = self.hotels.get_hotel("H1")
        self.assertEqual(loaded.available_rooms, 7)