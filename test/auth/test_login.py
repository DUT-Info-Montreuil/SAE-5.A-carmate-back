import unittest

from api.worker.auth.exceptions import EmailFormatInvalid, CredentialInvalid
from api.worker.auth.models import CredentialDTO, TokenDTO
from api.worker.auth.use_case.login import Login
from database.exceptions import NotFound
from mock import InMemoryUserRepository, InMemoryTokenRepository


class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.login = Login(InMemoryUserRepository(), InMemoryTokenRepository())

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
        with self.assertRaises(EmailFormatInvalid):
            self.login.worker(credential)


if __name__ == '__main__':
    unittest.main()
