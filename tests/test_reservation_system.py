"""
Unit tests for Reservation System (Actividad 6.2 - Ejercicio 3).

Requirements covered:
- unittest usage
- >= 5 negative test cases
- file persistence via JSON
- invalid file data handling prints errors and continues
"""

# pylint: disable=consider-using-with, too-many-public-methods

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from source.reservation_system import (
    Customer,
    Hotel,
    Reservation,
    ReservationStorage,
)


class ReservationSystemTests(unittest.TestCase):
    """Test suite for Hotel, Customer and Reservation behaviors."""

    def setUp(self) -> None:
        """Create a temporary storage directory per test."""
        self.tmp = tempfile.TemporaryDirectory()
        base_dir = Path(self.tmp.name)
        self.storage = ReservationStorage.from_base_dir(base_dir)

    def tearDown(self) -> None:
        """Cleanup temporary directory."""
        self.tmp.cleanup()

    def test_create_and_display_customer_success(self) -> None:
        """Create customer and read it back."""
        created = Customer.create_customer(
            self.storage,
            "C1",
            "Arturo",
            "a@a.com",
        )
        self.assertTrue(created)

        info = Customer.display_customer_information(self.storage, "C1")
        self.assertIsNotNone(info)
        self.assertEqual(info["customer_id"], "C1")

    def test_create_and_display_hotel_success(self) -> None:
        """Create hotel and read it back."""
        created = Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 2)
        self.assertTrue(created)

        info = Hotel.display_hotel_information(self.storage, "H1")
        self.assertIsNotNone(info)
        self.assertEqual(info["hotel_id"], "H1")
        self.assertEqual(info["available_rooms"], 2)

    def test_reservation_and_cancel_success(self) -> None:
        """Reserve and cancel a reservation updates availability."""
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 1)

        reservation_id = Hotel.reserve_a_room(
            self.storage,
            "H1",
            "C1",
            "2026-01-01",
            "2026-01-02",
        )
        self.assertIsNotNone(reservation_id)

        hotel_info = Hotel.display_hotel_information(self.storage, "H1")
        self.assertEqual(hotel_info["available_rooms"], 0)

        cancelled = Hotel.cancel_a_reservation(
            self.storage, str(reservation_id))
        self.assertTrue(cancelled)

        hotel_info2 = Hotel.display_hotel_information(self.storage, "H1")
        self.assertEqual(hotel_info2["available_rooms"], 1)

    def test_delete_customer_success(self) -> None:
        """Delete existing customer."""
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")

        deleted = Customer.delete_customer(self.storage, "C1")
        self.assertTrue(deleted)

        buf = StringIO()
        with redirect_stdout(buf):
            info = Customer.display_customer_information(self.storage, "C1")
        self.assertIsNone(info)
        self.assertIn("ERROR:", buf.getvalue())

    def test_modify_customer_success(self) -> None:
        """Modify customer name/email."""
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")

        updated = Customer.modify_customer_information(
            self.storage,
            "C1",
            name="Arturo A",
            email="aa@a.com",
        )
        self.assertTrue(updated)

        info = Customer.display_customer_information(self.storage, "C1")
        self.assertEqual(info["name"], "Arturo A")
        self.assertEqual(info["email"], "aa@a.com")

    def test_delete_hotel_success(self) -> None:
        """Delete existing hotel."""
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 2)

        deleted = Hotel.delete_hotel(self.storage, "H1")
        self.assertTrue(deleted)

        buf = StringIO()
        with redirect_stdout(buf):
            info = Hotel.display_hotel_information(self.storage, "H1")
        self.assertIsNone(info)
        self.assertIn("ERROR:", buf.getvalue())

    def test_modify_hotel_success(self) -> None:
        """Modify hotel name and expand rooms."""
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 2)

        updated = Hotel.modify_hotel_information(
            self.storage,
            "H1",
            name="Hotel 1",
            total_rooms=3,
        )
        self.assertTrue(updated)

        info = Hotel.display_hotel_information(self.storage, "H1")
        self.assertEqual(info["name"], "Hotel 1")
        self.assertEqual(info["total_rooms"], 3)
        self.assertEqual(info["available_rooms"], 3)

    def test_negative_create_customer_invalid_id(self) -> None:
        """Negative: create customer with empty ID."""
        buf = StringIO()
        with redirect_stdout(buf):
            created = Customer.create_customer(
                self.storage, "", "Name", "x@x.com")
        self.assertFalse(created)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_create_hotel_invalid_rooms(self) -> None:
        """Negative: create hotel with non-positive total rooms."""
        buf = StringIO()
        with redirect_stdout(buf):
            created = Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 0)
        self.assertFalse(created)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_reserve_room_missing_customer(self) -> None:
        """Negative: reserve with non-existing customer."""
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 1)

        buf = StringIO()
        with redirect_stdout(buf):
            reservation_id = Hotel.reserve_a_room(
                self.storage,
                "H1",
                "C404",
                "2026-01-01",
                "2026-01-02",
            )
        self.assertIsNone(reservation_id)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_reserve_room_no_availability(self) -> None:
        """Negative: reserve when hotel has no rooms available."""
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 1)

        first = Reservation.create_reservation(
            self.storage,
            "C1",
            "H1",
            "2026-01-01",
            "2026-01-02",
        )
        self.assertIsNotNone(first)

        buf = StringIO()
        with redirect_stdout(buf):
            second = Reservation.create_reservation(
                self.storage,
                "C1",
                "H1",
                "2026-01-03",
                "2026-01-04",
            )
        self.assertIsNone(second)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_cancel_nonexistent_reservation(self) -> None:
        """Negative: cancel reservation that does not exist."""
        buf = StringIO()
        with redirect_stdout(buf):
            cancelled = Reservation.cancel_reservation(self.storage, "R404")
        self.assertFalse(cancelled)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_modify_hotel_reduce_below_reserved(self) -> None:
        """Negative: reduce total rooms below reserved count."""
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 2)

        res_id = Reservation.create_reservation(
            self.storage,
            "C1",
            "H1",
            "2026-01-01",
            "2026-01-02",
        )
        self.assertIsNotNone(res_id)

        buf = StringIO()
        with redirect_stdout(buf):
            updated = Hotel.modify_hotel_information(
                self.storage,
                "H1",
                total_rooms=0,
            )
        self.assertFalse(updated)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_cancel_same_reservation_twice(self) -> None:
        """Negative: cancelling twice should fail second time."""
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 1)

        res_id = Reservation.create_reservation(
            self.storage,
            "C1",
            "H1",
            "2026-01-01",
            "2026-01-02",
        )
        self.assertIsNotNone(res_id)

        first = Reservation.cancel_reservation(self.storage, str(res_id))
        self.assertTrue(first)

        buf = StringIO()
        with redirect_stdout(buf):
            second = Reservation.cancel_reservation(self.storage, str(res_id))
        self.assertFalse(second)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_duplicate_customer_id(self) -> None:
        """Negative: creating the same customer twice should fail."""
        ok1 = Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")
        self.assertTrue(ok1)

        buf = StringIO()
        with redirect_stdout(buf):
            ok2 = Customer.create_customer(
                self.storage,
                "C1",
                "Arturo 2",
                "b@b.com",
            )
        self.assertFalse(ok2)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_modify_customer_not_found(self) -> None:
        """Negative: modifying a non-existing customer should fail."""
        buf = StringIO()
        with redirect_stdout(buf):
            updated = Customer.modify_customer_information(
                self.storage,
                "C404",
                name="X",
                email="x@x.com",
            )
        self.assertFalse(updated)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_delete_hotel_not_found(self) -> None:
        """Negative: deleting a non-existing hotel should fail."""
        buf = StringIO()
        with redirect_stdout(buf):
            deleted = Hotel.delete_hotel(self.storage, "H404")
        self.assertFalse(deleted)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_reserve_room_missing_hotel(self) -> None:
        """Negative: reserve a room in a non-existing hotel."""
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")

        buf = StringIO()
        with redirect_stdout(buf):
            res_id = Hotel.reserve_a_room(
                self.storage,
                "H404",
                "C1",
                "2026-01-01",
                "2026-01-02",
            )
        self.assertIsNone(res_id)
        self.assertIn("ERROR:", buf.getvalue())

    def test_invalid_json_file_is_handled_and_execution_continues(
        self,
    ) -> None:
        invalid_path = Path(self.tmp.name) / "hotels.json"
        invalid_path.write_text("{ invalid json", encoding="utf-8")

        buf = StringIO()
        with redirect_stdout(buf):
            hotels = self.storage.load_hotels()
        self.assertEqual(hotels, [])
        self.assertIn("ERROR:", buf.getvalue())

        ok = Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 1)
        self.assertTrue(ok)

    def test_invalid_json_type_is_handled(self) -> None:
        """JSON type dict instead of list should not crash."""
        hotels_path = Path(self.tmp.name) / "hotels.json"
        hotels_path.write_text('{"hotel_id": "H1"}', encoding="utf-8")

        buf = StringIO()
        with redirect_stdout(buf):
            hotels = self.storage.load_hotels()
        self.assertEqual(hotels, [])
        self.assertIn("ERROR:", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
