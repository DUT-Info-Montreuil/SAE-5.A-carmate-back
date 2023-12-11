import io
import os
import unittest
from datetime import datetime
from hashlib import sha512

from api.worker.admin import DocumentType, ValidationStatus
from api.worker.admin.use_case.get_license_to_validate import GetLicenseToValidate
from api.worker.user import AccountStatus
from database.exceptions import NotFound, DocumentAlreadyChecked
from database.schemas import UserTable, LicenseTable
from mock import InMemoryUserRepository, InMemoryLicenseRepository


class GetLicensesToValidateTestCase(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), "../res/teacher-contract.png"), "rb") as f:
            self.license_img = io.BytesIO(f.read())

        self.user_repo = InMemoryUserRepository()
        self.license_repo = InMemoryLicenseRepository(self.user_repo)
        self.inserted_user = UserTable(2, "Fred", "Mercury", "ssa@example.com", sha512("password".encode('utf-8')).digest(), AccountStatus.Teacher.name, datetime.now(), None)
        self.user_repo.users.append(self.inserted_user)
        self.get_licenses_to_validate = GetLicenseToValidate(self.license_repo)

    def test_it_gets_the_license(self):
        license_table = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 2)
        self.license_repo.licenses.append(license_table)

        try:
            fetched_license = self.get_licenses_to_validate.worker(1)

            self.assertIsNotNone(license)
            self.assertEqual(self.inserted_user.first_name, fetched_license.first_name)
            self.assertEqual(self.inserted_user.last_name, fetched_license.last_name)
            self.assertEqual(self.inserted_user.account_status, fetched_license.account_type)
            self.assertEqual(fetched_license.license_type, DocumentType.Basic.name)
            self.assertEqual(fetched_license.document, self.license_img)

        except Exception as e:
            self.fail(e)

    def test_it_raise_value_error_when_document_id_none(self):
        license_table = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 2)
        self.license_repo.licenses.append(license_table)

        try:

            with self.assertRaises(ValueError):
                self.get_licenses_to_validate.worker()

            with self.assertRaises(ValueError):
                self.get_licenses_to_validate.worker(None)

        except Exception as e:
            self.fail(e)

    def test_it_raise_value_error_when_document_id_invalid(self):
        license_table = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 2)
        self.license_repo.licenses.append(license_table)

        try:

            with self.assertRaises(NotFound):
                self.get_licenses_to_validate.worker(915132)

        except Exception as e:
            self.fail(e)

    def test_it_raise_document_already_checked_when_document_is_not_pending(self):
        license_table1 = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Rejected.name, datetime.now(), 2)
        license_table2 = LicenseTable(2, self.license_img, DocumentType.Basic.name, ValidationStatus.Approved.name, datetime.now(), 2)

        self.license_repo.licenses.append(license_table1)
        self.license_repo.licenses.append(license_table2)

        try:
            with self.assertRaises(DocumentAlreadyChecked):
                self.get_licenses_to_validate.worker(1)

            with self.assertRaises(DocumentAlreadyChecked):
                self.get_licenses_to_validate.worker(2)

        except Exception as e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()
