import unittest

from api.worker.user.use_case import GetHistory
from api.exceptions import UserNotFound
from database.schemas import ReserveCarpoolingTable


class HistoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.get_history = GetHistory()
    
    def test_history_with_carpooling_booked(self):
        self.assertListEqual(self.get_history.worker("token-booking-valid"), [ReserveCarpoolingTable(5, 20, 123456, passenger_code_validated=True)])

    def test_history_with_no_carpooling_book(self):
        self.assertListEqual(self.get_history.worker("token-no-booking-valid"), [])

    def test_history_of_invalid_user(self):
        with self.assertRaises(UserNotFound):
            self.get_history.worker("token-does-not-exist")
