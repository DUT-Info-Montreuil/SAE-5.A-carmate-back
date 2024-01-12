import unittest
from datetime import datetime, timedelta, time
from hashlib import sha512

from api.worker.carpooling.use_case.check_for_matching_passenger_scheduled import CheckForMatchingPassengerScheduled
from database.exceptions import NotFound
from database.schemas import TokenTable, DriverProfileTable, UserTable, PassengerScheduledCarpoolingTable, Weekday, \
    CarpoolingTable, PassengerProfileTable


class CheckForMatchingPassengerScheduledTest(unittest.TestCase):
    def setUp(self):
        self.use_case = CheckForMatchingPassengerScheduled()
        self.use_case.propose_scheduled_carpooling_repository.propose_scheduled_carpoolings.append(
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
        self.use_case.carpooling_repository.carpoolings.append(
            CarpoolingTable(
                79481382,
                [2, 999],
                [4, 4],
                4,
                0,
                False,
                datetime.strptime("3000-01-15 10:00:00", "%Y-%m-%d %H:%M:%S"),
                2,
            )
        )
        self.use_case.carpooling_repository.carpoolings.append(
            CarpoolingTable(
                9999,
                [49, 3],
                [49, 4],
                4,
                0,
                False,
                datetime.strptime("2025-07-16 10:00:00", "%Y-%m-%d %H:%M:%S"),
                2,
            )
        )
        for i in range(10):
            self.use_case.user_repository.users.append(
                UserTable(
                          99996 +i,
                          'John',
                          'Doe',
                          'john.doe@example.com',
                          b'hashed_password',
                          'rdm',
                          datetime.now())
            )
            self.use_case.passenger_profile_repository.passenger_profiles.append(
                PassengerProfileTable(
                    999944 + i,
                    '',
                    datetime.now(),
                    i)
            )
        self.use_case.user_repository.users.append(
            UserTable(
                      99999,
                      'John',
                      'Doe',
                      'john.doe@example.com',
                      b'hashed_password',
                      'rdm',
                      datetime.now())
        )
        self.use_case.passenger_profile_repository.passenger_profiles.append(
            PassengerProfileTable(
                9999,
                '',
                datetime.now(),
                99999)
        )

    def test_fails_id_carpooling_id_not_found(self):
        with self.assertRaises(NotFound):
            self.use_case.worker(8915648974)

    def test_do_nothing_when_no_match_found(self):
        base_len = len(self.use_case.booking_carpooling_repository.reserved_carpoolings)
        self.use_case.worker(79481382)
        self.assertEqual(len(self.use_case.booking_carpooling_repository.reserved_carpoolings), base_len)

    def test_create_reservation(self):
        base_len = len(self.use_case.booking_carpooling_repository.reserved_carpoolings)
        self.use_case.worker(9999)
        self.assertEqual(len(self.use_case.booking_carpooling_repository.reserved_carpoolings), base_len + 1)
        self.assertEqual(self.use_case.booking_carpooling_repository.reserved_carpoolings[base_len].user_id, 99999)
        self.assertEqual(self.use_case.booking_carpooling_repository.reserved_carpoolings[base_len].carpooling_id, 9999)

    def test_create_multiple_reservation(self):
        self.use_case.propose_scheduled_carpooling_repository.propose_scheduled_carpoolings.append(
            PassengerScheduledCarpoolingTable(
                1900,
                "test",
                [49, 3],
                [49, 4],
                datetime.strptime("2025-02-11", "%Y-%m-%d").date(),
                datetime.strptime("2026-05-08", "%Y-%m-%d").date(),
                time(10, 0),
                [Weekday.Wednesday],
                999944 + 1
            )
        )

        base_len = len(self.use_case.booking_carpooling_repository.reserved_carpoolings)
        self.use_case.worker(9999)
        self.assertEqual(len(self.use_case.booking_carpooling_repository.reserved_carpoolings), base_len + 2)

    def test_creates_maximum_of_max_passenger_reservations(self):
        for i in range(10):
            self.use_case.propose_scheduled_carpooling_repository.propose_scheduled_carpoolings.append(
                PassengerScheduledCarpoolingTable(
                    1900,
                    "test",
                    [49, 3],
                    [49, 4],
                    datetime.strptime("2025-02-11", "%Y-%m-%d").date(),
                    datetime.strptime("2026-05-08", "%Y-%m-%d").date(),
                    time(10, 0),
                    [Weekday.Wednesday],
                    999944 + i
                )
            )

        base_len = len(self.use_case.booking_carpooling_repository.reserved_carpoolings)
        self.use_case.worker(9999)
        self.assertEqual(len(self.use_case.booking_carpooling_repository.reserved_carpoolings), base_len + 4)
