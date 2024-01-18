import random
import unittest

from datetime import datetime, timedelta, time
from hashlib import sha512

from api.worker import AccountStatus
from api.worker.carpooling.use_case import BookingCarpooling
from api.exceptions import (
    CarpoolingAlreadyFull,
    CarpoolingCanceled,
    CarpoolingBookedTooLate,
    CarpoolingNotFound,
    BookingCanNotBeCreated
)
from database.schemas import (
    UserTable,
    PassengerProfileTable,
    TokenTable,
    ReserveCarpoolingTable,
    CarpoolingTable,
    DriverProfileTable,
    PassengerScheduledCarpoolingTable,
    Weekday
)


class BookingCarpoolingTestCase(unittest.TestCase):
    def setUp(self):
        self.booking_carpooling = BookingCarpooling()
        self.booking_carpooling.user_repository.users.append(
            UserTable(9999, "John", "Doe", "qdcsidbcisd", sha512("password".encode()).digest(), AccountStatus.Student.name, None),
        )
        self.booking_carpooling.passenger_profile_repository.passenger_profiles.append(
            PassengerProfileTable(9999, '', datetime.now(), 9999),
        )
        self.booking_carpooling.driver_profile_repository.driver_profiles.append(
            DriverProfileTable(9999, '', datetime.now(), 9999),
        )
        self.booking_carpooling.token_repository.tokens.append(
            TokenTable(sha512("token-user-test".encode()).digest(), datetime.now() + timedelta(days=1), 9999),
        )

    def test_regular_usage(self):
        self.assertIsNotNone(self.booking_carpooling.worker("token-user-test", 3))

    def test_already_full(self):
        with self.assertRaises(CarpoolingAlreadyFull):
            self.booking_carpooling.worker("token-user-test", 1)

    def test_canceled(self):
        with self.assertRaises(CarpoolingCanceled):
            self.booking_carpooling.worker("token-user-test", 27)

    def test_too_late(self):
        with self.assertRaises(CarpoolingBookedTooLate):
            self.booking_carpooling.worker("token-user-test", 28)

    def test_not_found(self):
        with self.assertRaises(CarpoolingNotFound):
            self.booking_carpooling.worker("token-user-test", 999)

    def test_conflict_with_reservation(self):
        self.booking_carpooling.booking_carpooling_repository.reserved_carpoolings.append(
            ReserveCarpoolingTable(9999, 9999, 123456)
        )
        self.booking_carpooling.carpooling_repository.carpoolings.append(
            CarpoolingTable(9999, [48.883078, 2.343902], [48.839678, 2.375806], 4, round(random.uniform(1, 50), 2), False, datetime.fromtimestamp(1831035836), 1),
        )
        self.booking_carpooling.carpooling_repository.carpoolings.append(
            CarpoolingTable(9696, [48.883078, 2.343902], [48.839678, 2.375806], 4, round(random.uniform(1, 50), 2), False, datetime.fromtimestamp(1831035836), 1)
        )
        with self.assertRaises(BookingCanNotBeCreated):
            self.booking_carpooling.worker("token-user-test", 9696)

    def test_conflict_with_carpool(self):
        self.booking_carpooling.carpooling_repository.carpoolings.append(
            CarpoolingTable(9999, [48.883078, 2.343902], [48.839678, 2.375806], 4, round(random.uniform(1, 50), 2), False, datetime.fromtimestamp(1831035836), 9999),
        )
        self.booking_carpooling.carpooling_repository.carpoolings.append(
            CarpoolingTable(9696, [48.883078, 2.343902], [48.839678, 2.375806], 4, round(random.uniform(1, 50), 2), False, datetime.fromtimestamp(1831035836), 1)
        )
        with self.assertRaises(BookingCanNotBeCreated):
            self.booking_carpooling.worker("token-user-test", 9696)

    def test_conflict_with_scheduled(self):
        self.booking_carpooling.carpooling_repository.carpoolings.append(
            CarpoolingTable(9696, [48.883078, 2.343902], [48.839678, 2.375806], 4, round(random.uniform(1, 50), 2), False, datetime.strptime("2025-06-13 10:00:00", "%Y-%m-%d %H:%M:%S"), 1)
        )

        self.booking_carpooling.propose_scheduled_carpooling_repository.propose_scheduled_carpoolings.append(
            PassengerScheduledCarpoolingTable(9999,
                                              '',
                                              [48.883078, 2.343902],
                                              [48.839678, 2.375806],
                                              datetime.strptime("2025-02-11", "%Y-%m-%d").date(),
                                              datetime.strptime("2026-05-08", "%Y-%m-%d").date(),
                                              time(10, 0),
                                              [Weekday.Friday],
                                              9999)
        )
        with self.assertRaises(BookingCanNotBeCreated):
            self.booking_carpooling.worker("token-user-test", 9696)
