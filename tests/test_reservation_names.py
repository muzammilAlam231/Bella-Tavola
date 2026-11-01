import datetime as dt
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from app.schemas import ReservationCreate


class ReservationNameTests(unittest.TestCase):
    def reservation(self, name):
        with patch("app.rules.now_local", return_value=dt.datetime(2026, 1, 1, 10)):
            return ReservationCreate(
                name=name,
                email="guest@example.com",
                phone="1234567890",
                party_size=2,
                reservation_date=dt.date(2026, 1, 2),
                reservation_time=dt.time(18),
            )

    def test_rejects_names_that_are_too_short_after_normalization(self):
        for name in ["  ", "\t\n", " A ", "\tA\n"]:
            with self.subTest(name=name), self.assertRaises(ValidationError):
                self.reservation(name)

    def test_collapses_whitespace_before_applying_length_limit(self):
        self.assertEqual(self.reservation("  Ada   Lovelace  ").name, "Ada Lovelace")
        self.assertEqual(self.reservation(" " * 100 + "Ada").name, "Ada")

    def test_preserves_valid_unicode_names(self):
        self.assertEqual(self.reservation("  José  ").name, "José")

    def test_rejects_non_string_names_as_validation_errors(self):
        for name in [None, 42, ["Ada"]]:
            with self.subTest(name=name), self.assertRaises(ValidationError):
                self.reservation(name)


if __name__ == "__main__":
    unittest.main()
