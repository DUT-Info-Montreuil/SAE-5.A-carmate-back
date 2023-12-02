import os
import io
import unittest

from api.exceptions import AccountAlreadyExist, LengthNameTooLong
from api.worker.user import AccountStatus
from api.worker.auth.models import CredentialDTO
from api.worker.auth.use_case import Register
from mock import InMemoryUserRepository, InMemoryTokenRepository, InMemoryLicenseRepository


class RegisterTestCase(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), "../res/student-card.png"), "rb") as f:
            self.student_card = io.BytesIO(f.read())
        with open(os.path.join(os.path.dirname(__file__), "../res/teacher-contract.png"), "rb") as f:
            self.teacher_contract = io.BytesIO(f.read())

        self.student_account_type = AccountStatus.Student
        self.teacher_account_type = AccountStatus.Teacher

        user_repository = InMemoryUserRepository()
        self.register = Register(user_repository,
                                 InMemoryTokenRepository(),
                                 InMemoryLicenseRepository(user_repository))

    def test_regular_usage_for_student(self):
        credential = CredentialDTO("Davina", "Mcgovern", "davina.mcgovern@email.com", "pwd")
        try:
            self.register.worker(credential, self.student_account_type, self.student_card)
        except Exception as e:
            self.fail(e)

    def test_regular_usage_for_teacher(self):
        credential = CredentialDTO("Piotre", "Mcgovern", "piotre.mcgovern@email.com", "pwd")
        try:
            self.register.worker(credential, self.teacher_account_type, self.teacher_contract)
        except Exception as e:
            self.fail(e)

    def test_duplicate_user(self):
        credential = CredentialDTO("Lewis", "Mccullough", "lewis.mccullough@email.com", "pwd")
        try:
            self.register.worker(credential, self.teacher_account_type, self.teacher_contract)
        except Exception as e:
            self.fail(e)

        with self.assertRaises(AccountAlreadyExist):
            self.register.worker(credential, self.teacher_account_type, self.teacher_contract)

    def test_oversize_first_name(self):
        credential = CredentialDTO("hkydj927KSVtZthgEivQK3Q2GXWtUAYtLlZi0wJFfRxzW7feTiFy61jRLoytXguKgzs7H1dAjAmv9Vxbo1MvFkY195Q0x81mNf1YkNSGfpj74ggiV22bcpK8JAOk8BebfqGMv9MYxETWghZbr6dfpRUKdEo040yiRjsoAu9RfVAu2612JalJyG5vTMiuKFPoZhHoU1HqedpkQT7jpyOIBZKamacTsCt8MvtqEzARYlUUBJNLDMRAsURSWCyb12xovJFwGHAcTGvwoALnXl7FHE3cVSKCoRkghZ8dLkWGcdca", "Mccullough", "lewis.mccullough@email.com", "pwd")

        with self.assertRaises(LengthNameTooLong):
            self.register.worker(credential, self.teacher_account_type, self.teacher_contract)

    def test_oversize_family_name(self):
        credential = CredentialDTO("Lewis", "hkydj927KSVtZthgEivQK3Q2GXWtUAYtLlZi0wJFfRxzW7feTiFy61jRLoytXguKgzs7H1dAjAmv9Vxbo1MvFkY195Q0x81mNf1YkNSGfpj74ggiV22bcpK8JAOk8BebfqGMv9MYxETWghZbr6dfpRUKdEo040yiRjsoAu9RfVAu2612JalJyG5vTMiuKFPoZhHoU1HqedpkQT7jpyOIBZKamacTsCt8MvtqEzARYlUUBJNLDMRAsURSWCyb12xovJFwGHAcTGvwoALnXl7FHE3cVSKCoRkghZ8dLkWGcdca", "lewis.mccullough@email.com", "pwd")

        with self.assertRaises(LengthNameTooLong):
            self.register.worker(credential, self.teacher_account_type, self.teacher_contract)


if __name__ == '__main__':
    unittest.main()
