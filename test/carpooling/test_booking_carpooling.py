import unittest

from api.worker.carpooling.use_case import BookingCarpooling
from api.exceptions import (
    CarpoolingAlreadyFull,
    CarpoolingCanceled,
    CarpoolingBookedTooLate,
    CarpoolingNotFound
)


class BookingCarpoolingTestCase(unittest.TestCase):
    def setUp(self):
        self.booking_carpooling = BookingCarpooling()

    def test_regular_usage(self):
        self.assertIsNotNone(self.booking_carpooling.worker("token-user-valid", 3))

    def test_already_full(self):
        with self.assertRaises(CarpoolingAlreadyFull):
            self.booking_carpooling.worker("token-user-valid", 1)

    def test_canceled(self):
        with self.assertRaises(CarpoolingCanceled):
            self.booking_carpooling.worker("token-user-valid", 27)

    def test_too_late(self):
        with self.assertRaises(CarpoolingBookedTooLate):
            self.booking_carpooling.worker("token-user-valid", 28)

    def test_not_found(self):
        with self.assertRaises(CarpoolingNotFound):
            self.booking_carpooling.worker("token-user-valid", 999)
