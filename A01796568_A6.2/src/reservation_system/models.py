"""
Domain models for the Reservation System.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Hotel:
    """Represents a hotel with room availability."""

    hotel_id: str
    name: str
    city: str
    total_rooms: int
    available_rooms: int

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Hotel":
        """Deserialize from dictionary."""
        return Hotel(
            hotel_id=str(data["hotel_id"]),
            name=str(data["name"]),
            city=str(data["city"]),
            total_rooms=int(data["total_rooms"]),
            available_rooms=int(data["available_rooms"]),
        )


@dataclass(frozen=True)
class Customer:
    """Represents a customer."""

    customer_id: str
    name: str
    email: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Customer":
        """Deserialize from dictionary."""
        return Customer(
            customer_id=str(data["customer_id"]),
            name=str(data["name"]),
            email=str(data["email"]),
        )


@dataclass(frozen=True)
class Reservation:
    """Represents a reservation between a customer and a hotel."""

    reservation_id: str
    customer_id: str
    hotel_id: str
    rooms_reserved: int
    status: str  # "active" or "cancelled"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Reservation":
        """Deserialize from dictionary."""
        return Reservation(
            reservation_id=str(data["reservation_id"]),
            customer_id=str(data["customer_id"]),
            hotel_id=str(data["hotel_id"]),
            rooms_reserved=int(data["rooms_reserved"]),
            status=str(data["status"]),
        )
