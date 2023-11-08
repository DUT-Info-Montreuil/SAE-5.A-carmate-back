import unittest

from api.worker.auth.models import CredentialDTO, TokenDTO
from api.worker.user.exceptions import *
from api.worker.user.use_case.login import Login
from database.exceptions import NotFound, CredentialInvalid
from mock.auth.in_memory_token_repository import InMemoryTokenRepository
from mock.user.in_memory_user_repository import InMemoryUserRepository


class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.login = Login(InMemoryUserRepository, InMemoryTokenRepository)

    def test_successful_login(self):
        credential = CredentialDTO("John", "Doe", "user@example.com", "password")
        try:
            token_obj = self.login.worker(credential)
            self.assertIsInstance(token_obj, TokenDTO)
        except Exception as e:
            self.fail(e)

    def test_invalid_email(self):
        credential = CredentialDTO("John", "Doe", "wrong@example.com", "password")
        with self.assertRaises(Exception) as context:
            self.login.worker(credential)

        self.assertTrue(context.exception, CredentialInvalid)
        self.assertTrue(context.exception, NotFound)

    def test_invalid_password(self):
        credential = CredentialDTO("John", "Doe", "user@example.com", "wrongpassword")
        with self.assertRaises(CredentialInvalid):
            self.login.worker(credential)

    def test_invalid_format_email(self):
        credential = CredentialDTO("John", "Doe", "user-example.com", "password")
        with self.assertRaises(EmailFormatInvalid) as context:
            self.login.worker(credential)


if __name__ == '__main__':
    unittest.main()

