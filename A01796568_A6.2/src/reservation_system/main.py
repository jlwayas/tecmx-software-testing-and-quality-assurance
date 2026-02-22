"""
Interactive CLI runner for the Reservation System using ./data JSON files.

Run:
  PYTHONPATH=src python -m reservation_system.main
"""

from __future__ import annotations

from pathlib import Path

from reservation_system.models import Customer, Hotel
from reservation_system.services import NotFoundError, ValidationError, build_services


def _prompt(text: str) -> str:
    """Prompt user input and strip whitespace."""
    return input(text).strip()


def _prompt_int(text: str) -> int:
    """Prompt user input for an integer, keep asking until valid."""
    while True:
        raw = _prompt(text)
        try:
            return int(raw)
        except ValueError:
            print("ERROR: Ingresa un número entero válido.")


def _print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def _ensure_data_files() -> Path:
    """
    Ensure ./data directory exists.
    JSON files are created automatically when saving for the first time.
    """
    base_dir = Path("data")
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def _list_hotels(hotels) -> None:
    """Print hotels."""
    _print_header("LISTA DE HOTELES")
    items = hotels.list_hotels()
    if not items:
        print("(Sin hoteles)")
        return
    for h in items:
        print(
            f"- ID={h.hotel_id} | {h.name} | {h.city} | "
            f"total={h.total_rooms} | disponibles={h.available_rooms}"
        )


def _create_hotel(hotels) -> None:
    """Create hotel."""
    _print_header("CREAR HOTEL")
    hotel_id = _prompt("Hotel ID: ")
    name = _prompt("Nombre: ")
    city = _prompt("Ciudad: ")
    total_rooms = _prompt_int("Total de habitaciones: ")
    available_rooms = _prompt_int("Habitaciones disponibles: ")

    hotels.create_hotel(
        Hotel(
            hotel_id=hotel_id,
            name=name,
            city=city,
            total_rooms=total_rooms,
            available_rooms=available_rooms,
        )
    )
    print("OK: Hotel creado.")


def _modify_hotel(hotels) -> None:
    """Modify hotel fields."""
    _print_header("MODIFICAR HOTEL")
    hotel_id = _prompt("Hotel ID a modificar: ")

    print("Deja vacío si no quieres cambiar el campo.")
    name = _prompt("Nuevo nombre: ")
    city = _prompt("Nueva ciudad: ")
    total_rooms_raw = _prompt("Nuevo total de habitaciones (int): ")
    available_raw = _prompt("Nuevas disponibles (int): ")

    updates = {}
    if name:
        updates["name"] = name
    if city:
        updates["city"] = city
    if total_rooms_raw:
        updates["total_rooms"] = int(total_rooms_raw)
    if available_raw:
        updates["available_rooms"] = int(available_raw)

    if not updates:
        print("INFO: No se enviaron cambios.")
        return

    hotels.modify_hotel(hotel_id, updates)
    print("OK: Hotel actualizado.")


def _delete_hotel(hotels) -> None:
    """Delete a hotel by ID."""
    _print_header("ELIMINAR HOTEL")
    hotel_id = _prompt("Hotel ID a eliminar: ")
    hotels.delete_hotel(hotel_id)
    print("OK: Hotel eliminado.")


def _list_customers(customers) -> None:
    """Print customers."""
    _print_header("LISTA DE CLIENTES")
    items = customers.list_customers()
    if not items:
        print("(Sin clientes)")
        return
    for c in items:
        print(f"- ID={c.customer_id} | {c.name} | {c.email}")


def _create_customer(customers) -> None:
    """Create customer."""
    _print_header("CREAR CLIENTE")
    customer_id = _prompt("Customer ID: ")
    name = _prompt("Nombre: ")
    email = _prompt("Email: ")

    customers.create_customer(Customer(customer_id=customer_id, name=name, email=email))
    print("OK: Cliente creado.")


def _modify_customer(customers) -> None:
    """Modify customer fields."""
    _print_header("MODIFICAR CLIENTE")
    customer_id = _prompt("Customer ID a modificar: ")

    print("Deja vacío si no quieres cambiar el campo.")
    name = _prompt("Nuevo nombre: ")
    email = _prompt("Nuevo email: ")

    updates = {}
    if name:
        updates["name"] = name
    if email:
        updates["email"] = email

    if not updates:
        print("INFO: No se enviaron cambios.")
        return

    customers.modify_customer(customer_id, updates)
    print("OK: Cliente actualizado.")


def _delete_customer(customers) -> None:
    """Delete customer by ID."""
    _print_header("ELIMINAR CLIENTE")
    customer_id = _prompt("Customer ID a eliminar: ")
    customers.delete_customer(customer_id)
    print("OK: Cliente eliminado.")


def _list_reservations(reservations) -> None:
    """Print reservations."""
    _print_header("LISTA DE RESERVACIONES")
    items = reservations.list_reservations()
    if not items:
        print("(Sin reservaciones)")
        return
    for r in items:
        print(
            f"- ID={r.reservation_id} | customer={r.customer_id} | "
            f"hotel={r.hotel_id} | rooms={r.rooms_reserved} | status={r.status}"
        )


def _create_reservation(reservations) -> None:
    """Create a reservation."""
    _print_header("CREAR RESERVACION")
    customer_id = _prompt("Customer ID: ")
    hotel_id = _prompt("Hotel ID: ")
    rooms = _prompt_int("Habitaciones a reservar: ")

    reservation_id = reservations.create_reservation(customer_id, hotel_id, rooms)
    print(f"OK: Reservación creada. ID={reservation_id}")


def _cancel_reservation(reservations) -> None:
    """Cancel an existing reservation."""
    _print_header("CANCELAR RESERVACION")
    reservation_id = _prompt("Reservation ID a cancelar: ")
    reservations.cancel_reservation(reservation_id)
    print("OK: Reservación cancelada.")


def _menu() -> None:
    """Main menu loop."""
    base_dir = _ensure_data_files()
    services = build_services(base_dir)
    hotels = services["hotels"]
    customers = services["customers"]
    reservations = services["reservations"]

    actions = {
        "1": ("Listar hoteles", lambda: _list_hotels(hotels)),
        "2": ("Crear hotel", lambda: _create_hotel(hotels)),
        "3": ("Modificar hotel", lambda: _modify_hotel(hotels)),
        "4": ("Eliminar hotel", lambda: _delete_hotel(hotels)),
        "5": ("Listar clientes", lambda: _list_customers(customers)),
        "6": ("Crear cliente", lambda: _create_customer(customers)),
        "7": ("Modificar cliente", lambda: _modify_customer(customers)),
        "8": ("Eliminar cliente", lambda: _delete_customer(customers)),
        "9": ("Listar reservaciones", lambda: _list_reservations(reservations)),
        "10": ("Crear reservación", lambda: _create_reservation(reservations)),
        "11": ("Cancelar reservación", lambda: _cancel_reservation(reservations)),
        "0": ("Salir", None),
    }

    while True:
        _print_header("RESERVATION SYSTEM - MENU")
        for key in sorted(actions.keys(), key=lambda x: int(x) if x.isdigit() else 999):
            print(f"{key}. {actions[key][0]}")

        choice = _prompt("\nSelecciona una opción: ")
        if choice == "0":
            print("Saliendo...")
            break

        action = actions.get(choice)
        if not action:
            print("ERROR: Opción inválida.")
            continue

        try:
            action[1]()  # run
        except (ValidationError, NotFoundError) as exc:
            print(f"ERROR: {exc}")
        except ValueError as exc:
            # For int conversions from input
            print(f"ERROR: {exc}")


def main() -> None:
    """Entry point."""
    _menu()


if __name__ == "__main__":
    main()
