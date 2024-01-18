import unittest

from datetime import datetime, timedelta
from hashlib import sha512

from api.exceptions import (
    CarpoolingNotFound,
    DriverNotFound,
    CarpoolingNotFromThisDriver,
    InvalidTimeToConfirmCode,
    CarpoolingCanceled,
    BookingNotFound
)
from api.worker import AccountStatus
from api.worker.carpooling.use_case import ConfirmPassengerCode
from database.schemas import (
    CarpoolingTable,
    DriverProfileTable,
    PassengerProfileTable,
    UserTable,
    TokenTable
)


class CheckForMatchingPassengerScheduledTest(unittest.TestCase):
    def setUp(self):
        self.use_case = ConfirmPassengerCode()
        self.valid_carpooling = CarpoolingTable(
                9999,
                [2, 999],
                [4, 4],
                4,
                0,
                False,
                datetime.now(),
                555,
            )
        self.canceled_carpooling = CarpoolingTable(
                99999,
                [2, 999],
                [4, 4],
                4,
                0,
                True,
                datetime.now(),
                555,
            )
        self.too_late_carpooling = CarpoolingTable(
                999999,
                [2, 999],
                [4, 4],
                4,
                0,
                False,
                datetime.now() - timedelta(hours=2),
                555,
            )
        self.too_early_carpooling = CarpoolingTable(
                9999999,
                [2, 999],
                [4, 4],
                4,
                0,
                False,
                datetime.now() + timedelta(hours=2),
                555,
            )

        self.use_case.driver_profile_repository.driver_profiles.append(
            DriverProfileTable(555, "no desc", datetime.now(), 1)
        )

        self.use_case.user_repository.users.append(
            UserTable(999, "Fred", "Mercury", "ssa@example.com", sha512("password".encode('utf-8')).digest(), AccountStatus.Teacher.name, datetime.now(), None)
        )
        self.use_case.token_repository.tokens.append(
            TokenTable(sha512("token-random-driver".encode()).digest(), datetime.now() + timedelta(days=1), 999),
        )
        self.use_case.driver_profile_repository.driver_profiles.append(
            DriverProfileTable(555, "no desc", datetime.now(), 3)
        )
        self.use_case.driver_profile_repository.driver_profiles.append(
            DriverProfileTable(666, "no desc", datetime.now(), 999)
        )

        self.use_case.carpooling_repository.carpoolings.append(self.valid_carpooling)
        self.use_case.carpooling_repository.carpoolings.append(self.canceled_carpooling)
        self.use_case.carpooling_repository.carpoolings.append(self.too_late_carpooling)
        self.use_case.carpooling_repository.carpoolings.append(self.too_early_carpooling)

        self.use_case.booking_carpooling_repository.insert(1, self.valid_carpooling.id, 123456)
        self.use_case.booking_carpooling_repository.insert(1, self.canceled_carpooling.id, 123456)
        self.use_case.booking_carpooling_repository.insert(1, self.too_late_carpooling.id, 123456)
        self.use_case.booking_carpooling_repository.insert(1, self.too_early_carpooling.id, 123456)

    def test_confirm_passenger_code(self):
        self.use_case.worker(9999, 123456, "token-admin-valid")

    def test_fails_carpooling_not_found(self):
        with self.assertRaises(CarpoolingNotFound):
            self.use_case.worker(999, 123456, "token-admin-valid")

    def test_fails_if_driver_not_found(self):
        with self.assertRaises(DriverNotFound):
            self.use_case.worker(self.valid_carpooling.id, 123456, "token-user-valid")

    def test_fails_if_carpooling_not_from_this_driver(self):
        with self.assertRaises(CarpoolingNotFromThisDriver):
            self.use_case.worker(self.valid_carpooling.id, 123456, "token-random-driver")

    def test_fails_if_too_late(self):
        with self.assertRaises(InvalidTimeToConfirmCode):
            self.use_case.worker(self.too_late_carpooling.id, 123456, "token-admin-valid")

    def test_fails_if_too_early(self):
        with self.assertRaises(InvalidTimeToConfirmCode):
            self.use_case.worker(self.too_early_carpooling.id, 123456, "token-admin-valid")

    def test_fails_if_carpooling_canceled(self):
        with self.assertRaises(CarpoolingCanceled):
            self.use_case.worker(self.canceled_carpooling.id, 123456, "token-admin-valid")

    def test_fails_if_booking_not_found(self):
        with self.assertRaises(BookingNotFound):
            self.use_case.worker(self.valid_carpooling.id, 999, "token-admin-valid")
