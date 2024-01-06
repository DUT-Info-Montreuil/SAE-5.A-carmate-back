import unittest

from api.worker.user.use_case.get_future_events import GetFutureEvents
from database.exceptions import NotFound


class FutureEventsTest(unittest.TestCase):
    def setUp(self):
        self.future_events = GetFutureEvents()

    def test_fails_if_user_not_found(self):
        with self.assertRaises(NotFound):
            self.future_events.worker("token-invalid-user")
