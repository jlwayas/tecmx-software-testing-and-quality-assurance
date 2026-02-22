"""Unit tests for HotelService."""

from reservation_system.models import Hotel
from reservation_system.services import ValidationError
from tests.base_test_case import BaseServiceTestCase


class TestHotelService(BaseServiceTestCase):
    """Tests for hotel CRUD and room management."""

    def test_create_and_get_hotel(self) -> None:
        """Creating a hotel persists it and it can be retrieved."""
        hotel = Hotel("H1", "Ritz", "CDMX", 10, 10)
        self.hotels.create_hotel(hotel)

        loaded = self.hotels.get_hotel("H1")
        self.assertEqual(loaded.name, "Ritz")

    def test_modify_hotel(self) -> None:
        """Modifying an existing hotel updates persisted fields."""
        self.hotels.create_hotel(Hotel("H1", "Ritz", "CDMX", 10, 10))
        self.hotels.modify_hotel("H1", {"name": "Ritz Updated", "available_rooms": 9})

        loaded = self.hotels.get_hotel("H1")
        self.assertEqual(loaded.name, "Ritz Updated")
        self.assertEqual(loaded.available_rooms, 9)

    def test_reserve_rooms_success(self) -> None:
        """Reserving rooms decreases available_rooms."""
        self.hotels.create_hotel(Hotel("H1", "Ritz", "CDMX", 10, 10))
        self.hotels.reserve_rooms("H1", 3)

        loaded = self.hotels.get_hotel("H1")
        self.assertEqual(loaded.available_rooms, 7)

    def test_reserve_rooms_not_enough(self) -> None:
        """Reserving more rooms than available raises ValidationError."""
        self.hotels.create_hotel(Hotel("H1", "Ritz", "CDMX", 2, 2))
        with self.assertRaises(ValidationError):
            self.hotels.reserve_rooms("H1", 3)

    def test_release_rooms_success(self) -> None:
        """Releasing rooms increases available_rooms without exceeding total_rooms."""
        self.hotels.create_hotel(Hotel("H1", "Ritz", "CDMX", 10, 5))
        self.hotels.release_rooms("H1", 2)

        loaded = self.hotels.get_hotel("H1")
        self.assertEqual(loaded.available_rooms, 7)
