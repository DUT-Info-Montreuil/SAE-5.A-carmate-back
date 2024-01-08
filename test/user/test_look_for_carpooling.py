import unittest
from datetime import datetime, timedelta, time
from hashlib import sha512

from api.worker.user.use_case.look_for_carpoolings import LookForCarpooling
from database.exceptions import NotFound
from database.schemas import CarpoolingTable, UserTable, PassengerProfileTable, TokenTable, \
    PassengerScheduledCarpoolingTable, Weekday


class CreatePassengerScheduledCarpoolingTest(unittest.TestCase):
    def setUp(self):
        self.look_for_carpooling = LookForCarpooling()
        self.look_for_carpooling.carpooling_repository.carpoolings.append(
            CarpoolingTable(
                9999,
                [49, 3],
                [49, 4],
                4,
                0,
                False,
                datetime.strptime("2025-07-09 10:00:00", "%Y-%m-%d %H:%M:%S"),
                2,
            )
        )
        self.look_for_carpooling.user_repository.users.append(
            UserTable(
                      99999,
                      'John',
                      'Doe',
                      'john.doe@example.com',
                      b'hashed_password',
                      'rdm',
                      datetime.now())
        )
        self.look_for_carpooling.passenger_profile_repository.passenger_profiles.append(
            PassengerProfileTable(
                                  9999,
                                  '',
                                  datetime.now(),
                                  99999)
        )
        self.look_for_carpooling.token_repository.tokens.append(
            TokenTable(sha512("from-test-new-user".encode()).digest(), datetime.now() + timedelta(days=1), 99999),
        )
        self.look_for_carpooling.propose_scheduled_carpooling_repository.propose_scheduled_carpoolings.append(
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


    def test_fails_if_scheduled_carpooling_not_found(self):
        with self.assertRaises(NotFound):
            self.look_for_carpooling.worker(1234587932)

    def test_create_reservation(self):
        base_len = len(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings)
        self.look_for_carpooling.worker(9999)
        self.assertEqual(len(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings), base_len + 1)
        self.assertEqual(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings[base_len].user_id, 99999)
        self.assertEqual(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings[base_len].carpooling_id, 9999)
        self.assertEqual(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings[base_len].passenger_code, 123456)

    def test_create_reservation_with_more_than_one_reservation(self):
        self.look_for_carpooling.carpooling_repository.carpoolings.append(
            CarpoolingTable(
                141478,
                [49, 3],
                [49, 4],
                4,
                0,
                False,
                datetime.strptime("2026-02-04 10:00:00", "%Y-%m-%d %H:%M:%S"),
                2,
            )
        )

        base_len = len(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings)
        self.look_for_carpooling.worker(9999)
        self.assertEqual(len(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings), base_len + 2)
        self.assertEqual(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings[base_len].user_id, 99999)
        self.assertEqual(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings[base_len].carpooling_id, 9999)
        self.assertEqual(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings[base_len].passenger_code, 123456)
        self.assertEqual(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings[base_len + 1].user_id, 99999)
        self.assertEqual(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings[base_len + 1].carpooling_id, 141478)
        self.assertEqual(self.look_for_carpooling.booking_carpooling_repository.reserved_carpoolings[base_len + 1].passenger_code, 123456)
