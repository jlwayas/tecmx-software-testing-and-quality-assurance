import tempfile
import unittest
from pathlib import Path

from reservation_system.models import Customer, Hotel
from reservation_system.services import NotFoundError, ValidationError, build_services


class TestReservationService(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp.name)
        services = build_services(self.data_dir)
        self.hotels = services["hotels"]
        self.customers = services["customers"]
        self.reservations = services["reservations"]

        self.hotels.create_hotel(Hotel("H1", "Ritz", "CDMX", 10, 10))
        self.customers.create_customer(Customer("C1", "Ana", "ana@test.com"))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_create_reservation_success(self) -> None:
        reservation_id = self.reservations.create_reservation("C1", "H1", 2)
        res = self.reservations.get_reservation(reservation_id)
        self.assertEqual(res.status, "active")

        hotel = self.hotels.get_hotel("H1")
        self.assertEqual(hotel.available_rooms, 8)

    def test_cancel_reservation_success(self) -> None:
        reservation_id = self.reservations.create_reservation("C1", "H1", 2)
        self.reservations.cancel_reservation(reservation_id)

        res = self.reservations.get_reservation(reservation_id)
        self.assertEqual(res.status, "cancelled")

        hotel = self.hotels.get_hotel("H1")
        self.assertEqual(hotel.available_rooms, 10)

    def test_create_reservation_invalid_customer(self) -> None:
        with self.assertRaises(NotFoundError):
            self.reservations.create_reservation("C404", "H1", 1)

    def test_cancel_reservation_twice_fails(self) -> None:
        reservation_id = self.reservations.create_reservation("C1", "H1", 1)
        self.reservations.cancel_reservation(reservation_id)
        with self.assertRaises(ValidationError):
            self.reservations.cancel_reservation(reservation_id)