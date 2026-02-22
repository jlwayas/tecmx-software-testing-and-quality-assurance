"""
Business services for managing hotels, customers, and reservations.
All operations persist to JSON files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from reservation_system.models import Customer, Hotel, Reservation
from reservation_system.storage import JsonStore


class NotFoundError(ValueError):
    """Raised when a requested entity does not exist."""


class ValidationError(ValueError):
    """Raised when business rules are violated."""


class HotelService:
    """CRUD and reservation-related operations for hotels."""

    def __init__(self, store: JsonStore) -> None:
        """Create a hotel service with a JSON store."""
        self._store = store

    def list_hotels(self) -> List[Hotel]:
        """Return all hotels from storage."""
        return self._store.load_items(Hotel.from_dict)

    def get_hotel(self, hotel_id: str) -> Hotel:
        """Return a hotel by id or raise NotFoundError."""
        for hotel in self.list_hotels():
            if hotel.hotel_id == hotel_id:
                return hotel
        raise NotFoundError(f"Hotel not found: {hotel_id}")

    def create_hotel(self, hotel: Hotel) -> None:
        """Persist a new hotel; raise ValidationError if it already exists."""
        hotels = self.list_hotels()
        if any(h.hotel_id == hotel.hotel_id for h in hotels):
            raise ValidationError(f"Hotel already exists: {hotel.hotel_id}")
        self._validate_rooms(hotel.total_rooms, hotel.available_rooms)
        hotels.append(hotel)
        self._save(hotels)

    def delete_hotel(self, hotel_id: str) -> None:
        """Delete a hotel by id; raise NotFoundError if missing."""
        hotels = self.list_hotels()
        new_hotels = [h for h in hotels if h.hotel_id != hotel_id]
        if len(new_hotels) == len(hotels):
            raise NotFoundError(f"Hotel not found: {hotel_id}")
        self._save(new_hotels)

    def modify_hotel(self, hotel_id: str, updates: Dict[str, Any]) -> None:
        """
        Modify an existing hotel with provided updates.

        Allowed keys: name, city, total_rooms, available_rooms.
        Raises NotFoundError if hotel does not exist, ValidationError on invalid rooms.
        """
        allowed = {"name", "city", "total_rooms", "available_rooms"}
        unknown = set(updates.keys()) - allowed
        if unknown:
            raise ValidationError(f"Unknown hotel fields: {sorted(unknown)}")

        hotels = self.list_hotels()
        updated_hotels: List[Hotel] = []
        found = False

        for hotel in hotels:
            if hotel.hotel_id != hotel_id:
                updated_hotels.append(hotel)
                continue

            found = True
            new_name = updates.get("name", hotel.name)
            new_city = updates.get("city", hotel.city)
            new_total = updates.get("total_rooms", hotel.total_rooms)
            new_avail = updates.get("available_rooms", hotel.available_rooms)

            new_total_int = int(new_total)
            new_avail_int = int(new_avail)
            self._validate_rooms(new_total_int, new_avail_int)

            updated_hotels.append(
                Hotel(
                    hotel_id=hotel.hotel_id,
                    name=str(new_name),
                    city=str(new_city),
                    total_rooms=new_total_int,
                    available_rooms=new_avail_int,
                )
            )

        if not found:
            raise NotFoundError(f"Hotel not found: {hotel_id}")

        self._save(updated_hotels)

    def reserve_rooms(self, hotel_id: str, rooms: int) -> None:
        """Reserve a number of rooms for a hotel; decreases availability."""
        if rooms <= 0:
            raise ValidationError("rooms must be > 0")
        hotel = self.get_hotel(hotel_id)
        if hotel.available_rooms < rooms:
            raise ValidationError("Not enough rooms available")
        self.modify_hotel(
            hotel_id,
            {"available_rooms": hotel.available_rooms - rooms},
        )

    def release_rooms(self, hotel_id: str, rooms: int) -> None:
        """Release a number of rooms back to availability; increases availability."""
        if rooms <= 0:
            raise ValidationError("rooms must be > 0")
        hotel = self.get_hotel(hotel_id)
        new_avail = hotel.available_rooms + rooms
        if new_avail > hotel.total_rooms:
            raise ValidationError("available_rooms cannot exceed total_rooms")
        self.modify_hotel(hotel_id, {"available_rooms": new_avail})

    @staticmethod
    def _validate_rooms(total_rooms: int, available_rooms: int) -> None:
        """Validate room counts are non-negative "
        "and availability does not exceed total."""
        if total_rooms < 0 or available_rooms < 0:
            raise ValidationError("rooms cannot be negative")
        if available_rooms > total_rooms:
            raise ValidationError("available_rooms cannot exceed total_rooms")

    def _save(self, hotels: List[Hotel]) -> None:
        """Persist hotel list to JSON store."""
        self._store.save_raw_list([h.to_dict() for h in hotels])


class CustomerService:
    """CRUD operations for customers."""

    def __init__(self, store: JsonStore) -> None:
        """Create a customer service with a JSON store."""
        self._store = store

    def list_customers(self) -> List[Customer]:
        """Return all customers from storage."""
        return self._store.load_items(Customer.from_dict)

    def get_customer(self, customer_id: str) -> Customer:
        """Return a customer by id or raise NotFoundError."""
        for customer in self.list_customers():
            if customer.customer_id == customer_id:
                return customer
        raise NotFoundError(f"Customer not found: {customer_id}")

    def create_customer(self, customer: Customer) -> None:
        """Persist a new customer; raise ValidationError if it already exists."""
        customers = self.list_customers()
        if any(c.customer_id == customer.customer_id for c in customers):
            raise ValidationError(f"Customer already exists: {customer.customer_id}")
        customers.append(customer)
        self._save(customers)

    def delete_customer(self, customer_id: str) -> None:
        """Delete a customer by id; raise NotFoundError if missing."""
        customers = self.list_customers()
        new_customers = [c for c in customers if c.customer_id != customer_id]
        if len(new_customers) == len(customers):
            raise NotFoundError(f"Customer not found: {customer_id}")
        self._save(new_customers)

    def modify_customer(self, customer_id: str, updates: Dict[str, Any]) -> None:
        """
        Modify an existing customer with provided updates.

        Allowed keys: name, email.
        """
        allowed = {"name", "email"}
        unknown = set(updates.keys()) - allowed
        if unknown:
            raise ValidationError(f"Unknown customer fields: {sorted(unknown)}")

        customers = self.list_customers()
        updated_customers: List[Customer] = []
        found = False

        for customer in customers:
            if customer.customer_id != customer_id:
                updated_customers.append(customer)
                continue

            found = True
            new_name = updates.get("name", customer.name)
            new_email = updates.get("email", customer.email)

            updated_customers.append(
                Customer(
                    customer_id=customer.customer_id,
                    name=str(new_name),
                    email=str(new_email),
                )
            )

        if not found:
            raise NotFoundError(f"Customer not found: {customer_id}")

        self._save(updated_customers)

    def _save(self, customers: List[Customer]) -> None:
        """Persist customer list to JSON store."""
        self._store.save_raw_list([c.to_dict() for c in customers])


class ReservationService:
    """Create/cancel reservations (Customer + Hotel)."""

    def __init__(
        self,
        store: JsonStore,
        hotel_service: HotelService,
        customer_service: CustomerService,
    ) -> None:
        """Create reservation service with references to hotel and customer services."""
        self._store = store
        self._hotel_service = hotel_service
        self._customer_service = customer_service

    def list_reservations(self) -> List[Reservation]:
        """Return all reservations from storage."""
        return self._store.load_items(Reservation.from_dict)

    def get_reservation(self, reservation_id: str) -> Reservation:
        """Return a reservation by id or raise NotFoundError."""
        for reservation in self.list_reservations():
            if reservation.reservation_id == reservation_id:
                return reservation
        raise NotFoundError(f"Reservation not found: {reservation_id}")

    def create_reservation(self, customer_id: str, hotel_id: str, rooms: int) -> str:
        """
        Create a reservation and reserve rooms in the hotel.

        Returns the reservation id.
        """
        self._customer_service.get_customer(customer_id)
        self._hotel_service.get_hotel(hotel_id)

        if rooms <= 0:
            raise ValidationError("rooms must be > 0")

        self._hotel_service.reserve_rooms(hotel_id, rooms)

        reservation_id = str(uuid4())
        reservation = Reservation(
            reservation_id=reservation_id,
            customer_id=customer_id,
            hotel_id=hotel_id,
            rooms_reserved=rooms,
            status="active",
        )

        reservations = self.list_reservations()
        reservations.append(reservation)
        self._save(reservations)
        return reservation_id

    def cancel_reservation(self, reservation_id: str) -> None:
        """Cancel an active reservation and release the reserved rooms."""
        reservations = self.list_reservations()
        updated: List[Reservation] = []
        found = False

        for reservation in reservations:
            if reservation.reservation_id != reservation_id:
                updated.append(reservation)
                continue

            found = True
            if reservation.status != "active":
                raise ValidationError("Reservation already cancelled")

            self._hotel_service.release_rooms(
                reservation.hotel_id,
                reservation.rooms_reserved,
            )

            updated.append(
                Reservation(
                    reservation_id=reservation.reservation_id,
                    customer_id=reservation.customer_id,
                    hotel_id=reservation.hotel_id,
                    rooms_reserved=reservation.rooms_reserved,
                    status="cancelled",
                )
            )

        if not found:
            raise NotFoundError(f"Reservation not found: {reservation_id}")

        self._save(updated)

    def _save(self, reservations: List[Reservation]) -> None:
        """Persist reservation list to JSON store."""
        self._store.save_raw_list([r.to_dict() for r in reservations])


def build_services(base_dir: Path) -> Dict[str, object]:
    """Factory to build services using a base directory for data files."""
    hotels_store = JsonStore(base_dir / "hotels.json")
    customers_store = JsonStore(base_dir / "customers.json")
    reservations_store = JsonStore(base_dir / "reservations.json")

    hotel_service = HotelService(hotels_store)
    customer_service = CustomerService(customers_store)
    reservation_service = ReservationService(
        reservations_store,
        hotel_service,
        customer_service,
    )

    return {
        "hotels": hotel_service,
        "customers": customer_service,
        "reservations": reservation_service,
    }
