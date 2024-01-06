import unittest
from datetime import datetime, timedelta
from hashlib import sha512

from api.worker import AccountStatus
from api.worker.user.use_case.get_future_events import GetFutureEvents
from database.exceptions import NotFound
from database.schemas import UserTable, TokenTable, PassengerProfileTable, DriverProfileTable, CarpoolingTable, \
    ReserveCarpoolingTable


class FutureEventsTest(unittest.TestCase):
    def setUp(self):
        self.future_events = GetFutureEvents()
        self.future_events.user_repository.users.append(
            UserTable(9999999,
                      "Fred",
                      "Mercury",
                      "ssa@example.com",
                      sha512("password".encode('utf-8')).digest(),
                      AccountStatus.Teacher.name,
                      datetime.now(), None
                      )
        )
        self.future_events.token_repository.tokens.append(
            TokenTable(sha512("token-future-tests".encode()).digest(),
                       datetime.now() + timedelta(days=1),
                       9999999)
        )
        self.future_events.passenger_profile_repository.passenger_profiles.append(
            PassengerProfileTable(312156, '', datetime.now(), 9999999)
        )
        self.future_events.driver_profile_repository.driver_profiles.append(
            DriverProfileTable(312156, '', datetime.now(), 9999999)
        )

    def test_fails_if_user_not_found(self):
        with self.assertRaises(NotFound):
            self.future_events.worker("token-invalid-user")

    def test_it_gets_future_carpoolings(self):
        self.future_events.carpooling_repository.carpoolings.append(
            CarpoolingTable(3636636, [1, 1], [1, 1], 4, 10.0, False, datetime.now() + timedelta(days=2), 312156)
        )
        future_events = self.future_events.worker("token-future-tests")
        self.assertEqual(1, len(future_events.proposed))
        self.assertEqual(3636636, future_events.proposed[0].carpooling_id)
        self.assertEqual(4, future_events.proposed[0].max_passengers)
        self.assertEqual(0, future_events.proposed[0].seats_taken)
        self.assertEqual([1, 1], future_events.proposed[0].starting_point)
        self.assertEqual([1, 1], future_events.proposed[0].destination)

    def test_it_gets_future_reservations(self):
        self.future_events.carpooling_repository.carpoolings.append(
            CarpoolingTable(3636636, [1, 1], [1, 1], 4, 10.0, False, datetime.now() + timedelta(days=2), 312156)
        )
        self.future_events.booking_carpooling_repository.reserved_carpoolings.append(
            ReserveCarpoolingTable(9999999, 3636636, 123456)
        )
        future_events = self.future_events.worker("token-future-tests")
        self.assertEqual(1, len(future_events.reserved))
        self.assertEqual(312156, future_events.reserved[0].driver_id)
        self.assertEqual(123456, future_events.reserved[0].passenger_code)

    def test_it_doesnt_get_past_carpoolings(self):
        self.future_events.carpooling_repository.carpoolings.append(
            CarpoolingTable(3636636, [1, 1], [1, 1], 4, 10.0, False, datetime.now() - timedelta(days=2), 312156)
        )
        future_events = self.future_events.worker("token-future-tests")
        self.assertEqual(0, len(future_events.proposed))

    def test_it_doesnt_get_past_reservations(self):
        self.future_events.carpooling_repository.carpoolings.append(
            CarpoolingTable(3636636, [1, 1], [1, 1], 4, 10.0, False, datetime.now() - timedelta(days=2), 312156)
        )
        self.future_events.booking_carpooling_repository.reserved_carpoolings.append(
            ReserveCarpoolingTable(9999999, 3636636, 123456, True)
        )
        future_events = self.future_events.worker("token-future-tests")
        self.assertEqual(0, len(future_events.reserved))

    def test_it_does_not_get_canceled_reservations(self):
        self.future_events.carpooling_repository.carpoolings.append(
            CarpoolingTable(3636636, [1, 1], [1, 1], 4, 10.0, False, datetime.now() + timedelta(days=2), 312156)
        )
        self.future_events.booking_carpooling_repository.reserved_carpoolings.append(
            ReserveCarpoolingTable(9999999, 3636636, 123456, canceled=True)
        )
        future_events = self.future_events.worker("token-future-tests")
        self.assertEqual(0, len(future_events.reserved))

    def test_it_does_not_get_canceled_carpooling(self):
        self.future_events.carpooling_repository.carpoolings.append(
            CarpoolingTable(3636636, [1, 1], [1, 1], 4, 10.0, False, datetime.now() + timedelta(days=2), 312156)
        )
        self.future_events.booking_carpooling_repository.reserved_carpoolings.append(
            ReserveCarpoolingTable(9999999, 3636636, 123456, canceled=True)
        )
        future_events = self.future_events.worker("token-future-tests")
        self.assertEqual(0, len(future_events.reserved))

    def test_it_doesnt_get_future_carpooling_canceled(self):
        self.future_events.carpooling_repository.carpoolings.append(
            CarpoolingTable(3636636, [1, 1], [1, 1], 4, 10.0, True, datetime.now() + timedelta(days=2), 312156)
        )
        future_events = self.future_events.worker("token-future-tests")
        self.assertEqual(0, len(future_events.proposed))
