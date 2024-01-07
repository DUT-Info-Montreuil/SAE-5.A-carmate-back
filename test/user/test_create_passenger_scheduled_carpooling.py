import unittest
from datetime import datetime, time, timedelta
from hashlib import sha512

from api.exceptions import PassengerNotFound, ScheduledCarpoolingCannotBeCreated
from api.worker.user.use_case import CreatePassengerScheduledCarpooling
from database.schemas import CarpoolingTable, Weekday, UserTable, PassengerProfileTable, TokenTable, \
    PassengerScheduledCarpoolingTable, ReserveCarpoolingTable, DriverProfileTable


class CreatePassengerScheduledCarpoolingTest(unittest.TestCase):
    def setUp(self):
        self.create_passenger_scheduled = CreatePassengerScheduledCarpooling()
        self.create_passenger_scheduled.carpooling_repository.carpoolings.append(
            CarpoolingTable(
                9999,
                [49, 3],
                [49, 4],
                4,
                0,
                False,
                datetime.strptime("2025-01-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
                2,
            )
        )
        self.create_passenger_scheduled.user_repository.users.append(
            UserTable(
                      99999,
                      'John',
                      'Doe',
                      'john.doe@example.com',
                      b'hashed_password',
                      'rdm',
                      datetime.now())
        )
        self.create_passenger_scheduled.passenger_profile_repository.passenger_profiles.append(
            PassengerProfileTable(
                                  9999,
                                  '',
                                  datetime.now(),
                                  99999)
        )
        self.create_passenger_scheduled.token_repository.tokens.append(
            TokenTable(sha512("from-test-new-user".encode()).digest(), datetime.now() + timedelta(days=1), 99999),
        )

    def test_throw_passenger_not_found(self):
        with self.assertRaises(PassengerNotFound):
            self.create_passenger_scheduled.worker(
                "test",
                [49, 3],
                [49, 4],
                datetime.strptime("2024-12-15", "%Y-%m-%d").date(),
                datetime.strptime("2025-12-15", "%Y-%m-%d").date(),
                time(10, 0),
                [Weekday.Wednesday],
                "token-invalid-user"
            )

    def test_fails_if_conflict_scheduled_carpooling(self):
        self.create_passenger_scheduled.propose_scheduled_carpooling_repository.propose_scheduled_carpoolings.append(
            PassengerScheduledCarpoolingTable(
                9999,
                "test",
                [49, 3],
                [49, 4],
                datetime.strptime("2025-02-11", "%Y-%m-%d").date(),
                datetime.strptime("2026-05-08", "%Y-%m-%d").date(),
                time(10, 0),
                [Weekday.Wednesday],
                9999
            )
        )

        with self.assertRaises(ScheduledCarpoolingCannotBeCreated):
            self.create_passenger_scheduled.worker(
                "test",
                [49, 3],
                [49, 4],
                datetime.strptime("2024-12-15", "%Y-%m-%d").date(),
                datetime.strptime("2025-12-15", "%Y-%m-%d").date(),
                time(10, 0),
                [Weekday.Wednesday],
                "from-test-new-user"
            )

    def test_fails_if_conflict_with_booked_carpooling(self):
        self.create_passenger_scheduled.booking_carpooling_repository.reserved_carpoolings.append(
            ReserveCarpoolingTable(99999, 9999, 123456),
        )

        with self.assertRaises(ScheduledCarpoolingCannotBeCreated):
            self.create_passenger_scheduled.worker(
                "test",
                [49, 3],
                [49, 4],
                datetime.strptime("2024-12-15", "%Y-%m-%d").date(),
                datetime.strptime("2025-12-15", "%Y-%m-%d").date(),
                time(10, 0),
                [Weekday.Wednesday],
                "from-test-new-user"
            )

    def test_fails_if_conflict_with_created_carpooling(self):
        self.create_passenger_scheduled.driver_profile_repository.driver_profiles.append(
            DriverProfileTable(
                                 9999,
                                 '',
                                 datetime.now(),
                                 99999)
            )

        with self.assertRaises(ScheduledCarpoolingCannotBeCreated):
            self.create_passenger_scheduled.worker(
                "test",
                [49, 3],
                [49, 4],
                datetime.strptime("2024-12-15", "%Y-%m-%d").date(),
                datetime.strptime("2025-12-15", "%Y-%m-%d").date(),
                time(10, 0),
                [Weekday.Wednesday],
                "from-test-new-user"
            )

    def test_it_inserts(self):
        self.create_passenger_scheduled.worker(
            "test",
            [49, 3],
            [49, 4],
            datetime.strptime("2024-12-15", "%Y-%m-%d").date(),
            datetime.strptime("2025-12-15", "%Y-%m-%d").date(),
            time(10, 0),
            [Weekday.Wednesday],
            "from-test-new-user"
        )

