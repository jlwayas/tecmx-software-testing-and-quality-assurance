"""Unit tests for ReservationService."""

from reservation_system.models import Customer, Hotel
from reservation_system.services import NotFoundError, ValidationError
from tests.base_test_case import BaseServiceTestCase


class TestReservationService(BaseServiceTestCase):
    """Tests for creating and cancelling reservations."""

    def setUp(self) -> None:
        """Build services and seed one hotel and one customer."""
        super().setUp()
        self.hotels.create_hotel(Hotel("H1", "Ritz", "CDMX", 10, 10))
        self.customers.create_customer(Customer("C1", "Ana", "ana@test.com"))

    def test_create_reservation_success(self) -> None:
        """Creating a reservation stores it and decreases hotel availability."""
        reservation_id = self.reservations.create_reservation("C1", "H1", 2)
        res = self.reservations.get_reservation(reservation_id)
        self.assertEqual(res.status, "active")

        hotel = self.hotels.get_hotel("H1")
        self.assertEqual(hotel.available_rooms, 8)

    def test_cancel_reservation_success(self) -> None:
        """Cancelling a reservation changes status and releases hotel rooms."""
        reservation_id = self.reservations.create_reservation("C1", "H1", 2)
        self.reservations.cancel_reservation(reservation_id)

        res = self.reservations.get_reservation(reservation_id)
        self.assertEqual(res.status, "cancelled")

        hotel = self.hotels.get_hotel("H1")
        self.assertEqual(hotel.available_rooms, 10)

    def test_create_reservation_invalid_customer(self) -> None:
        """Creating a reservation with a missing customer raises NotFoundError."""
        with self.assertRaises(NotFoundError):
            self.reservations.create_reservation("C404", "H1", 1)

    def test_cancel_reservation_twice_fails(self) -> None:
        """Cancelling the same reservation twice raises ValidationError."""
        reservation_id = self.reservations.create_reservation("C1", "H1", 1)
        self.reservations.cancel_reservation(reservation_id)

        with self.assertRaises(ValidationError):
            self.reservations.cancel_reservation(reservation_id)
