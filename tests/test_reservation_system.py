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
from unittest.mock import patch

from source.reservation_system import (
    Customer,
    Hotel,
    Reservation,
    ReservationStorage,
)


class ReservationSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.tmp_dir.name)

        self.storage = ReservationStorage.from_base_dir(self.base_dir)

        (self.base_dir / "hotels.json").write_text("[]", encoding="utf-8")
        (self.base_dir / "customers.json").write_text("[]", encoding="utf-8")
        (self.base_dir / "reservations.json").write_text(
            "[]",
            encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_create_and_display_customer_success(self) -> None:
        ok = Customer.create_customer(
            self.storage,
            "C1",
            "Arturo",
            "a@a.com",
        )
        self.assertTrue(ok)

        info = Customer.display_customer_information(self.storage, "C1")
        self.assertIsNotNone(info)
        self.assertEqual(info["customer_id"], "C1")
        self.assertEqual(info["name"], "Arturo")
        self.assertEqual(info["email"], "a@a.com")

    def test_create_and_display_hotel_success(self) -> None:
        ok = Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 3)
        self.assertTrue(ok)

        info = Hotel.display_hotel_information(self.storage, "H1")
        self.assertIsNotNone(info)
        self.assertEqual(info["hotel_id"], "H1")
        self.assertEqual(info["name"], "Hotel Uno")
        self.assertEqual(info["total_rooms"], 3)
        self.assertEqual(info["available_rooms"], 3)

    def test_delete_customer_success(self) -> None:
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")

        ok = Customer.delete_customer(self.storage, "C1")
        self.assertTrue(ok)

        info = Customer.display_customer_information(self.storage, "C1")
        self.assertIsNone(info)

    def test_delete_hotel_success(self) -> None:
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 2)

        ok = Hotel.delete_hotel(self.storage, "H1")
        self.assertTrue(ok)

        info = Hotel.display_hotel_information(self.storage, "H1")
        self.assertIsNone(info)

    def test_invalid_customers_json_is_handled(self) -> None:
        (self.base_dir / "customers.json").write_text("{", encoding="utf-8")

        buf = StringIO()
        with redirect_stdout(buf):
            customers = self.storage.load_customers()

        self.assertEqual(customers, [])
        self.assertIn("ERROR:", buf.getvalue())

    def test_invalid_hotels_json_is_handled_and_continues(self) -> None:
        (self.base_dir / "hotels.json").write_text("{", encoding="utf-8")

        buf = StringIO()
        with redirect_stdout(buf):
            hotels = self.storage.load_hotels()

        self.assertEqual(hotels, [])
        self.assertIn("ERROR:", buf.getvalue())

    def test_invalid_json_type_is_handled(self) -> None:
        (self.base_dir / "hotels.json").write_text("{}", encoding="utf-8")

        buf = StringIO()
        with redirect_stdout(buf):
            hotels = self.storage.load_hotels()

        self.assertEqual(hotels, [])
        self.assertIn("ERROR:", buf.getvalue())

    def test_invalid_reservations_json_is_handled(self) -> None:
        (self.base_dir / "reservations.json").write_text("{", encoding="utf-8")

        buf = StringIO()
        with redirect_stdout(buf):
            reservations = self.storage.load_reservations()

        self.assertEqual(reservations, [])
        self.assertIn("ERROR:", buf.getvalue())

    def test_modify_customer_success(self) -> None:
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")

        ok = Customer.modify_customer_information(
            self.storage,
            "C1",
            name="Arturo A",
            email="aa@a.com",
        )
        self.assertTrue(ok)

        info = Customer.display_customer_information(self.storage, "C1")
        self.assertEqual(info["name"], "Arturo A")
        self.assertEqual(info["email"], "aa@a.com")

    def test_modify_hotel_success(self) -> None:
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 2)

        ok = Hotel.modify_hotel_information(
            self.storage,
            "H1",
            name="Hotel Uno Plus",
            total_rooms=4,
        )
        self.assertTrue(ok)

        info = Hotel.display_hotel_information(self.storage, "H1")
        self.assertEqual(info["name"], "Hotel Uno Plus")
        self.assertEqual(info["total_rooms"], 4)
        self.assertEqual(info["available_rooms"], 4)

    def test_negative_cancel_nonexistent_reservation(self) -> None:
        buf = StringIO()
        with redirect_stdout(buf):
            ok = Reservation.cancel_reservation(self.storage, "NOEXIST")

        self.assertFalse(ok)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_cancel_same_reservation_twice(self) -> None:
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

        ok1 = Reservation.cancel_reservation(self.storage, str(res_id))
        self.assertTrue(ok1)

        buf = StringIO()
        with redirect_stdout(buf):
            ok2 = Reservation.cancel_reservation(self.storage, str(res_id))

        self.assertFalse(ok2)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_create_customer_invalid_id(self) -> None:
        buf = StringIO()
        with redirect_stdout(buf):
            ok = Customer.create_customer(
                self.storage,
                "",
                "Arturo",
                "a@a.com",
            )

        self.assertFalse(ok)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_create_hotel_invalid_rooms(self) -> None:
        buf = StringIO()
        with redirect_stdout(buf):
            ok = Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 0)

        self.assertFalse(ok)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_delete_hotel_not_found(self) -> None:
        buf = StringIO()
        with redirect_stdout(buf):
            ok = Hotel.delete_hotel(self.storage, "H404")

        self.assertFalse(ok)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_duplicate_customer_id(self) -> None:
        ok1 = Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")
        self.assertTrue(ok1)

        buf = StringIO()
        with redirect_stdout(buf):
            ok2 = Customer.create_customer(self.storage, "C1", "X", "x@x.com")

        self.assertFalse(ok2)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_modify_customer_not_found(self) -> None:
        buf = StringIO()
        with redirect_stdout(buf):
            ok = Customer.modify_customer_information(
                self.storage,
                "C404",
                name="New",
            )

        self.assertFalse(ok)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_modify_hotel_reduce_below_reserved(self) -> None:
        Customer.create_customer(self.storage, "C1", "A", "a@a.com")
        Customer.create_customer(self.storage, "C2", "B", "b@b.com")
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 2)

        r1 = Reservation.create_reservation(
            self.storage,
            "C1",
            "H1",
            "2026-01-01",
            "2026-01-02",
        )
        r2 = Reservation.create_reservation(
            self.storage,
            "C2",
            "H1",
            "2026-01-03",
            "2026-01-04",
        )
        self.assertIsNotNone(r1)
        self.assertIsNotNone(r2)

        buf = StringIO()
        with redirect_stdout(buf):
            ok = Hotel.modify_hotel_information(
                self.storage,
                "H1",
                total_rooms=1,
            )

        self.assertFalse(ok)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_reserve_room_missing_customer(self) -> None:
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 1)

        buf = StringIO()
        with redirect_stdout(buf):
            res_id = Reservation.create_reservation(
                self.storage,
                "C404",
                "H1",
                "2026-01-01",
                "2026-01-02",
            )

        self.assertIsNone(res_id)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_reserve_room_missing_hotel(self) -> None:
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")

        buf = StringIO()
        with redirect_stdout(buf):
            res_id = Reservation.create_reservation(
                self.storage,
                "C1",
                "H404",
                "2026-01-01",
                "2026-01-02",
            )

        self.assertIsNone(res_id)
        self.assertIn("ERROR:", buf.getvalue())

    def test_negative_reserve_room_no_availability(self) -> None:
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 1)

        ok_id = Reservation.create_reservation(
            self.storage,
            "C1",
            "H1",
            "2026-01-01",
            "2026-01-02",
        )
        self.assertIsNotNone(ok_id)

        buf = StringIO()
        with redirect_stdout(buf):
            res_id = Reservation.create_reservation(
                self.storage,
                "C1",
                "H1",
                "2026-01-03",
                "2026-01-04",
            )

        self.assertIsNone(res_id)
        self.assertIn("ERROR:", buf.getvalue())

    def test_reservation_and_cancel_success(self) -> None:
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

        info1 = Hotel.display_hotel_information(self.storage, "H1")
        self.assertEqual(info1["available_rooms"], 0)

        ok = Reservation.cancel_reservation(self.storage, str(res_id))
        self.assertTrue(ok)

        info2 = Hotel.display_hotel_information(self.storage, "H1")
        self.assertEqual(info2["available_rooms"], 1)

    def test_storage_skips_non_dict_records(self) -> None:
        hotels_path = self.base_dir / "hotels.json"
        hotels_path.write_text('[{"hotel_id":"H1"}, 123]', encoding="utf-8")

        buf = StringIO()
        with redirect_stdout(buf):
            hotels = self.storage.load_hotels()

        self.assertEqual(len(hotels), 1)
        self.assertEqual(hotels[0].get("hotel_id"), "H1")
        self.assertIn("ERROR:", buf.getvalue())

    def test_storage_read_oserror_is_handled(self) -> None:
        buf = StringIO()
        with patch.object(
            self.storage.hotels_path,
            "read_text",
            side_effect=OSError("read boom"),
        ):
            with redirect_stdout(buf):
                hotels = self.storage.load_hotels()

        self.assertEqual(hotels, [])
        self.assertIn("ERROR:", buf.getvalue())

    def test_storage_save_typeerror_is_handled(self) -> None:
        bad_records = [{"x": set([1])}]

        buf = StringIO()
        with redirect_stdout(buf):
            ok = self.storage.save_hotels(bad_records)

        self.assertFalse(ok)
        self.assertIn("ERROR:", buf.getvalue())

    def test_customer_create_invalid_name_and_email(self) -> None:
        buf1 = StringIO()
        with redirect_stdout(buf1):
            ok1 = Customer.create_customer(self.storage, "C1", "", "a@a.com")
        self.assertFalse(ok1)
        self.assertIn("ERROR:", buf1.getvalue())

        buf2 = StringIO()
        with redirect_stdout(buf2):
            ok2 = Customer.create_customer(self.storage, "C2", "Arturo", "")
        self.assertFalse(ok2)
        self.assertIn("ERROR:", buf2.getvalue())

    def test_display_customer_invalid_id(self) -> None:
        buf = StringIO()
        with redirect_stdout(buf):
            info = Customer.display_customer_information(self.storage, "")
        self.assertIsNone(info)
        self.assertIn("ERROR:", buf.getvalue())

    def test_display_hotel_invalid_id(self) -> None:
        buf = StringIO()
        with redirect_stdout(buf):
            info = Hotel.display_hotel_information(self.storage, "")
        self.assertIsNone(info)
        self.assertIn("ERROR:", buf.getvalue())

    def test_reservation_invalid_dates_are_rejected(self) -> None:
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 1)

        buf1 = StringIO()
        with redirect_stdout(buf1):
            res1 = Reservation.create_reservation(
                self.storage,
                "C1",
                "H1",
                "",
                "2026-01-02",
            )
        self.assertIsNone(res1)
        self.assertIn("ERROR:", buf1.getvalue())

        buf2 = StringIO()
        with redirect_stdout(buf2):
            res2 = Reservation.create_reservation(
                self.storage,
                "C1",
                "H1",
                "2026-01-01",
                "",
            )
        self.assertIsNone(res2)
        self.assertIn("ERROR:", buf2.getvalue())

    def test_create_reservation_fails_if_save_hotels_fails(self) -> None:
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 1)

        buf = StringIO()
        with patch.object(self.storage, "save_hotels", return_value=False):
            with redirect_stdout(buf):
                res_id = Reservation.create_reservation(
                    self.storage,
                    "C1",
                    "H1",
                    "2026-01-01",
                    "2026-01-02",
                )

        self.assertIsNone(res_id)
        self.assertIn("ERROR:", buf.getvalue())

    def test_create_reservation_rolls_back_if_save_reservations_fails(
        self,
    ) -> None:
        Customer.create_customer(self.storage, "C1", "Arturo", "a@a.com")
        Hotel.create_hotel(self.storage, "H1", "Hotel Uno", 1)

        buf = StringIO()
        with patch.object(
            self.storage,
            "save_reservations",
            return_value=False,
        ):
            with redirect_stdout(buf):
                res_id = Reservation.create_reservation(
                    self.storage,
                    "C1",
                    "H1",
                    "2026-01-01",
                    "2026-01-02",
                )

        self.assertIsNone(res_id)
        self.assertIn("ERROR:", buf.getvalue())

        hotel_info = Hotel.display_hotel_information(self.storage, "H1")
        self.assertEqual(hotel_info["available_rooms"], 1)

    def test_cancel_reservation_hotel_missing_marks_cancelled(self) -> None:
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

        hotels = self.storage.load_hotels()
        hotels = [h for h in hotels if h.get("hotel_id") != "H1"]
        self.storage.save_hotels(hotels)

        buf = StringIO()
        with redirect_stdout(buf):
            ok = Reservation.cancel_reservation(self.storage, str(res_id))

        self.assertFalse(ok)
        self.assertIn("ERROR:", buf.getvalue())

        reservations = self.storage.load_reservations()
        rec = None
        for r in reservations:
            if r.get("reservation_id") == str(res_id):
                rec = r
                break

        self.assertIsNotNone(rec)
        self.assertEqual(rec.get("status"), "cancelled")

    def test_cancel_reservation_fails_if_availability_already_full(
        self,
    ) -> None:
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

        hotels = self.storage.load_hotels()
        hotel = hotels[0]
        hotel["available_rooms"] = hotel["total_rooms"]
        self.storage.save_hotels(hotels)

        buf = StringIO()
        with redirect_stdout(buf):
            ok = Reservation.cancel_reservation(self.storage, str(res_id))

        self.assertFalse(ok)
        self.assertIn("ERROR:", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
