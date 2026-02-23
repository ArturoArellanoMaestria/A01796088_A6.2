"""
Reservation System - Actividad 6.2 (Ejercicio 3)

Implementa:
- Hotel, Customer, Reservation
- Persistencia en archivos JSON
- Manejo de datos inválidos en archivo: imprime error y continúa
- Métodos CRUD + reservar/cancelar
"""
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-return-statements

"""
Reservation System - Actividad 6.2 (Ejercicio 3)

Implementa:
- Hotel, Customer, Reservation
- Persistencia en archivos JSON
- Manejo de datos inválidos en archivo: imprime error y continúa
- Métodos CRUD + reservar/cancelar
"""

# pylint: disable=R0913,R0917,R0911

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


def _is_non_empty_str(value: Any) -> bool:
    """Return True if value is a non-empty string."""
    return isinstance(value, str) and value.strip() != ""


def _print_error(message: str) -> None:
    """Print errors in console as required by the assignment."""
    print(f"ERROR: {message}")


class ReservationStorage:
    """
    JSON file storage for hotels, customers and reservations.

    The storage never crashes on invalid file data:
    it prints an error and returns an empty list.
    """

    def __init__(
        self,
        hotels_path: Path,
        customers_path: Path,
        reservations_path: Path,
    ) -> None:
        self.hotels_path = Path(hotels_path)
        self.customers_path = Path(customers_path)
        self.reservations_path = Path(reservations_path)

        self._ensure_file(self.hotels_path)
        self._ensure_file(self.customers_path)
        self._ensure_file(self.reservations_path)

    @classmethod
    def from_base_dir(cls, base_dir: Path) -> "ReservationStorage":
        """Create storage using default filenames inside base_dir."""
        base_dir = Path(base_dir)
        return cls(
            hotels_path=base_dir / "hotels.json",
            customers_path=base_dir / "customers.json",
            reservations_path=base_dir / "reservations.json",
        )

    def _ensure_file(self, path: Path) -> None:
        """Ensure the JSON file exists; if not, create an empty list file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text("[]", encoding="utf-8")
        except OSError as exc:
            _print_error(f"Cannot create file '{path}': {exc}")

    def _load_list(self, path: Path, label: str) -> List[Dict[str, Any]]:
        """Load a list of dict records from JSON file."""
        try:
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)

            if not isinstance(data, list):
                _print_error(
                    f"Invalid data type in '{label}' file. "
                    "Expected JSON list; using empty list."
                )
                return []

            clean: List[Dict[str, Any]] = []
            for item in data:
                if isinstance(item, dict):
                    clean.append(item)
                else:
                    _print_error(
                        f"Invalid record in '{label}' file (not an object). "
                        "Skipping record."
                    )
            return clean

        except json.JSONDecodeError as exc:
            _print_error(
                f"Invalid JSON in '{label}' file '{path.name}': {exc}. "
                "Using empty list."
            )
            return []
        except OSError as exc:
            _print_error(f"Cannot read '{label}' file '{path.name}': {exc}")
            return []

    def _save_list(
        self,
        path: Path,
        label: str,
        records: List[Dict[str, Any]],
    ) -> bool:
        """Save list of dict records to JSON file."""
        try:
            path.write_text(
                json.dumps(records, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return True
        except (TypeError, OSError) as exc:
            _print_error(f"Cannot save '{label}' file '{path.name}': {exc}")
            return False

    def load_hotels(self) -> List[Dict[str, Any]]:
        """Load hotels records."""
        return self._load_list(self.hotels_path, "hotels")

    def save_hotels(self, records: List[Dict[str, Any]]) -> bool:
        """Save hotels records."""
        return self._save_list(self.hotels_path, "hotels", records)

    def load_customers(self) -> List[Dict[str, Any]]:
        """Load customers records."""
        return self._load_list(self.customers_path, "customers")

    def save_customers(self, records: List[Dict[str, Any]]) -> bool:
        """Save customers records."""
        return self._save_list(self.customers_path, "customers", records)

    def load_reservations(self) -> List[Dict[str, Any]]:
        """Load reservations records."""
        return self._load_list(self.reservations_path, "reservations")

    def save_reservations(self, records: List[Dict[str, Any]]) -> bool:
        """Save reservations records."""
        return self._save_list(self.reservations_path, "reservations", records)


def _find_record(
    records: List[Dict[str, Any]],
    key: str,
    value: str,
) -> Optional[Dict[str, Any]]:
    """Find first record with records[i][key] == value."""
    for record in records:
        if record.get(key) == value:
            return record
    return None


@dataclass
class Customer:
    """Customer entity and persistence behaviors."""

    customer_id: str
    name: str
    email: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
        }

    @staticmethod
    def _validate_fields(customer_id: Any, name: Any, email: Any) -> bool:
        """Validate basic customer fields."""
        if not _is_non_empty_str(customer_id):
            _print_error("Customer ID must be a non-empty string.")
            return False
        if not _is_non_empty_str(name):
            _print_error("Customer name must be a non-empty string.")
            return False
        if not _is_non_empty_str(email):
            _print_error("Customer email must be a non-empty string.")
            return False
        return True

    @classmethod
    def create_customer(
        cls,
        storage: ReservationStorage,
        customer_id: str,
        name: str,
        email: str,
    ) -> bool:
        """Create and persist a customer."""
        if not cls._validate_fields(customer_id, name, email):
            return False

        customers = storage.load_customers()
        if _find_record(customers, "customer_id", customer_id) is not None:
            _print_error(f"Customer '{customer_id}' already exists.")
            return False

        customers.append(cls(customer_id, name, email).to_dict())
        return storage.save_customers(customers)

    @classmethod
    def delete_customer(
        cls,
        storage: ReservationStorage,
        customer_id: str,
    ) -> bool:
        """Delete a customer by ID."""
        if not _is_non_empty_str(customer_id):
            _print_error("Customer ID must be a non-empty string.")
            return False

        customers = storage.load_customers()
        before = len(customers)
        customers = [c for c in customers if c.get("customer_id") != customer_id]

        if len(customers) == before:
            _print_error(f"Customer '{customer_id}' does not exist.")
            return False

        return storage.save_customers(customers)

    @classmethod
    def display_customer_information(
        cls,
        storage: ReservationStorage,
        customer_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Return customer info dict (and prints error if missing)."""
        if not _is_non_empty_str(customer_id):
            _print_error("Customer ID must be a non-empty string.")
            return None

        customers = storage.load_customers()
        customer = _find_record(customers, "customer_id", customer_id)

        if customer is None:
            _print_error(f"Customer '{customer_id}' not found.")
            return None

        return dict(customer)

    @classmethod
    def modify_customer_information(
        cls,
        storage: ReservationStorage,
        customer_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> bool:
        """Modify customer name/email."""
        if not _is_non_empty_str(customer_id):
            _print_error("Customer ID must be a non-empty string.")
            return False

        if name is not None and not _is_non_empty_str(name):
            _print_error("Customer name must be a non-empty string.")
            return False
        if email is not None and not _is_non_empty_str(email):
            _print_error("Customer email must be a non-empty string.")
            return False

        customers = storage.load_customers()
        customer = _find_record(customers, "customer_id", customer_id)

        if customer is None:
            _print_error(f"Customer '{customer_id}' not found.")
            return False

        if name is not None:
            customer["name"] = name
        if email is not None:
            customer["email"] = email

        return storage.save_customers(customers)


@dataclass
class Hotel:
    """Hotel entity and persistence behaviors."""

    hotel_id: str
    name: str
    total_rooms: int
    available_rooms: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "hotel_id": self.hotel_id,
            "name": self.name,
            "total_rooms": self.total_rooms,
            "available_rooms": self.available_rooms,
        }

    @staticmethod
    def _validate_fields(hotel_id: Any, name: Any, total_rooms: Any) -> bool:
        """Validate basic hotel fields."""
        if not _is_non_empty_str(hotel_id):
            _print_error("Hotel ID must be a non-empty string.")
            return False
        if not _is_non_empty_str(name):
            _print_error("Hotel name must be a non-empty string.")
            return False
        if not isinstance(total_rooms, int) or total_rooms <= 0:
            _print_error("Total rooms must be an integer > 0.")
            return False
        return True

    @classmethod
    def create_hotel(
        cls,
        storage: ReservationStorage,
        hotel_id: str,
        name: str,
        total_rooms: int,
    ) -> bool:
        """Create and persist a hotel."""
        if not cls._validate_fields(hotel_id, name, total_rooms):
            return False

        hotels = storage.load_hotels()
        if _find_record(hotels, "hotel_id", hotel_id) is not None:
            _print_error(f"Hotel '{hotel_id}' already exists.")
            return False

        hotel = cls(hotel_id, name, total_rooms, total_rooms)
        hotels.append(hotel.to_dict())
        return storage.save_hotels(hotels)

    @classmethod
    def delete_hotel(cls, storage: ReservationStorage, hotel_id: str) -> bool:
        """Delete a hotel by ID."""
        if not _is_non_empty_str(hotel_id):
            _print_error("Hotel ID must be a non-empty string.")
            return False

        hotels = storage.load_hotels()
        before = len(hotels)
        hotels = [h for h in hotels if h.get("hotel_id") != hotel_id]

        if len(hotels) == before:
            _print_error(f"Hotel '{hotel_id}' does not exist.")
            return False

        return storage.save_hotels(hotels)

    @classmethod
    def display_hotel_information(
        cls,
        storage: ReservationStorage,
        hotel_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Return hotel info dict (and prints error if missing)."""
        if not _is_non_empty_str(hotel_id):
            _print_error("Hotel ID must be a non-empty string.")
            return None

        hotels = storage.load_hotels()
        hotel = _find_record(hotels, "hotel_id", hotel_id)

        if hotel is None:
            _print_error(f"Hotel '{hotel_id}' not found.")
            return None

        return dict(hotel)

    @classmethod
    def modify_hotel_information(
        cls,
        storage: ReservationStorage,
        hotel_id: str,
        name: Optional[str] = None,
        total_rooms: Optional[int] = None,
    ) -> bool:
        """Modify hotel name/total rooms safely."""
        if not _is_non_empty_str(hotel_id):
            _print_error("Hotel ID must be a non-empty string.")
            return False

        if name is not None and not _is_non_empty_str(name):
            _print_error("Hotel name must be a non-empty string.")
            return False

        if total_rooms is not None and (
            not isinstance(total_rooms, int) or total_rooms <= 0
        ):
            _print_error("Total rooms must be an integer > 0.")
            return False

        hotels = storage.load_hotels()
        hotel = _find_record(hotels, "hotel_id", hotel_id)

        if hotel is None:
            _print_error(f"Hotel '{hotel_id}' not found.")
            return False

        if name is not None:
            hotel["name"] = name

        if total_rooms is not None:
            current_total = int(hotel.get("total_rooms", 0))
            current_available = int(hotel.get("available_rooms", 0))
            reserved = current_total - current_available

            if total_rooms < reserved:
                _print_error(
                    "Cannot reduce total rooms below already reserved rooms."
                )
                return False

            delta = total_rooms - current_total
            hotel["total_rooms"] = total_rooms
            hotel["available_rooms"] = current_available + delta

        return storage.save_hotels(hotels)

    @classmethod
    def reserve_a_room(
        cls,
        storage: ReservationStorage,
        hotel_id: str,
        customer_id: str,
        start_date: str,
        end_date: str,
    ) -> Optional[str]:
        """Reserve a room (wrapper)."""
        return Reservation.create_reservation(
            storage=storage,
            customer_id=customer_id,
            hotel_id=hotel_id,
            start_date=start_date,
            end_date=end_date,
        )

    @classmethod
    def cancel_a_reservation(
        cls,
        storage: ReservationStorage,
        reservation_id: str,
    ) -> bool:
        """Cancel a reservation (wrapper)."""
        return Reservation.cancel_reservation(storage, reservation_id)


@dataclass
class Reservation:
    """Reservation entity and persistence behaviors."""

    reservation_id: str
    customer_id: str
    hotel_id: str
    start_date: str
    end_date: str
    status: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "reservation_id": self.reservation_id,
            "customer_id": self.customer_id,
            "hotel_id": self.hotel_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
        }

    @staticmethod
    def _validate_fields(
        customer_id: Any,
        hotel_id: Any,
        start_date: Any,
        end_date: Any,
    ) -> bool:
        """Validate reservation inputs."""
        if not _is_non_empty_str(customer_id):
            _print_error("Customer ID must be a non-empty string.")
            return False
        if not _is_non_empty_str(hotel_id):
            _print_error("Hotel ID must be a non-empty string.")
            return False
        if not _is_non_empty_str(start_date):
            _print_error("Start date must be a non-empty string.")
            return False
        if not _is_non_empty_str(end_date):
            _print_error("End date must be a non-empty string.")
            return False
        return True

    @classmethod
    def create_reservation(
        cls,
        storage: ReservationStorage,
        customer_id: str,
        hotel_id: str,
        start_date: str,
        end_date: str,
    ) -> Optional[str]:
        """
        Create a reservation (Customer, Hotel).

        Rules:
        - Customer and Hotel must exist
        - Hotel must have availability
        - Updates hotel availability and saves reservation
        """
        if not cls._validate_fields(customer_id, hotel_id, start_date, end_date):
            return None

        customers = storage.load_customers()
        if _find_record(customers, "customer_id", customer_id) is None:
            _print_error(f"Customer '{customer_id}' does not exist.")
            return None

        hotels = storage.load_hotels()
        hotel = _find_record(hotels, "hotel_id", hotel_id)
        if hotel is None:
            _print_error(f"Hotel '{hotel_id}' does not exist.")
            return None

        available = int(hotel.get("available_rooms", 0))
        if available <= 0:
            _print_error(f"Hotel '{hotel_id}' has no available rooms.")
            return None

        reservations = storage.load_reservations()
        reservation_id = str(uuid.uuid4())
        reservation = cls(
            reservation_id=reservation_id,
            customer_id=customer_id,
            hotel_id=hotel_id,
            start_date=start_date,
            end_date=end_date,
            status="active",
        )

        hotel["available_rooms"] = available - 1

        if not storage.save_hotels(hotels):
            _print_error("Failed to save hotels file while reserving.")
            return None

        reservations.append(reservation.to_dict())
        if not storage.save_reservations(reservations):
            _print_error("Failed to save reservations file while reserving.")
            hotel["available_rooms"] = available
            storage.save_hotels(hotels)
            return None

        return reservation_id

    @classmethod
    def cancel_reservation(
        cls,
        storage: ReservationStorage,
        reservation_id: str,
    ) -> bool:
        """
        Cancel a reservation.

        Rules:
        - Reservation must exist and be active
        - Increments hotel's available rooms
        """
        if not _is_non_empty_str(reservation_id):
            _print_error("Reservation ID must be a non-empty string.")
            return False

        reservations = storage.load_reservations()
        reservation = _find_record(reservations, "reservation_id", reservation_id)

        if reservation is None:
            _print_error(f"Reservation '{reservation_id}' not found.")
            return False

        if reservation.get("status") != "active":
            _print_error(f"Reservation '{reservation_id}' is not active.")
            return False

        hotel_id = str(reservation.get("hotel_id", ""))
        hotels = storage.load_hotels()
        hotel = _find_record(hotels, "hotel_id", hotel_id)

        if hotel is None:
            _print_error("Hotel for this reservation was not found.")
            reservation["status"] = "cancelled"
            storage.save_reservations(reservations)
            return False

        current_available = int(hotel.get("available_rooms", 0))
        total_rooms = int(hotel.get("total_rooms", 0))

        if current_available >= total_rooms:
            _print_error("Hotel availability is already full; cannot cancel.")
            return False

        reservation["status"] = "cancelled"
        hotel["available_rooms"] = current_available + 1

        if not storage.save_hotels(hotels):
            _print_error("Failed to save hotels file while cancelling.")
            return False

        return storage.save_reservations(reservations)
        