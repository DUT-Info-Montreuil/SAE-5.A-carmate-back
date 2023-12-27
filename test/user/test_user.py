import unittest

from api.exceptions import UserNotFound
from api.worker.user.use_case.get_user import GetUser


class UserTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.get_user = GetUser()

    def test_get_user_from_token(self):
        self.assertIsNotNone(self.get_user.worker(token="token-user-valid"))

    def test_get_user_from_id(self):
        self.assertIsNotNone(self.get_user.worker(user_id=1))

    def test_get_user_from_wrong_token(self):
        with self.assertRaises(UserNotFound):
            self.get_user.worker(token="token-invalid")

    def test_get_user_from_wrong_id(self):
        with self.assertRaises(UserNotFound):
            self.get_user.worker(user_id=-1)
