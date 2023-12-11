import io
import os
import unittest

from datetime import datetime
from hashlib import sha512

from api.worker.admin import ValidationStatus, DocumentType
from api.worker.admin.use_case.get_licenses_to_validate import GetLicensesToValidate
from api.worker.user import AccountStatus
from database.schemas import UserTable, LicenseTable
from mock import InMemoryLicenseRepository, InMemoryUserRepository


class GetLicensesToValidateTestCase(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), "../res/teacher-contract.png"), "rb") as f:
            self.license_img = io.BytesIO(f.read())

        self.user_repo = InMemoryUserRepository()
        self.license_repo = InMemoryLicenseRepository(self.user_repo)
        self.license_repo_base_size = len(self.license_repo.licenses)
        self.user_repo.users.append(
            UserTable(999, "Fred", "Mercury", "ssa@example.com", sha512("password".encode('utf-8')).digest(), AccountStatus.Teacher.name, datetime.now(), None)
        )
        self.get_licenses_to_validate = GetLicensesToValidate(self.license_repo)

    def test_successful_fetch_student_license(self):
        license_table = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 0)
        user_0 = self.user_repo.get_user_by_id(0)
        self.license_repo.licenses.append(license_table)
        try:
            licenses = self.get_licenses_to_validate.worker()["items"]
            last_inserted_license = licenses[len(licenses) - 1]
            self.assertEqual(1 + self.license_repo_base_size, len(licenses))
            self.assertEqual(user_0.first_name, last_inserted_license.first_name)
            self.assertEqual(user_0.last_name, last_inserted_license.last_name)
            self.assertEqual(license_table.id, last_inserted_license.document_id)
            self.assertEqual(user_0.account_status, last_inserted_license.account_type)
            self.assertEqual(DocumentType.Basic.name, last_inserted_license.license_type)
        except Exception as e:
            self.fail(e)

    def test_successful_fetch_multiple_licenses(self):
        license_table1 = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 0)
        license_table2 = LicenseTable(2, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 999)

        user_0 = self.user_repo.get_user_by_id(0)
        user_999 = self.user_repo.get_user_by_id(999)

        self.license_repo.licenses.append(license_table1)
        self.license_repo.licenses.append(license_table2)

        try:
            licenses = self.get_licenses_to_validate.worker()["items"]

            last_inserted_license = licenses[len(licenses) - 1]
            before_last_inserted_license = licenses[len(licenses) - 2]

            self.assertEqual(len(licenses), 2 + self.license_repo_base_size)

            self.assertEqual(user_999.first_name, last_inserted_license.first_name)
            self.assertEqual(user_999.last_name, last_inserted_license.last_name)
            self.assertEqual(license_table2.id, last_inserted_license.document_id)
            self.assertEqual(user_999.account_status, last_inserted_license.account_type)
            self.assertEqual(DocumentType.Basic.name, last_inserted_license.license_type)

            self.assertEqual(user_0.first_name, before_last_inserted_license.first_name)
            self.assertEqual(user_0.last_name, before_last_inserted_license.last_name)
            self.assertEqual(license_table1.id, before_last_inserted_license.document_id)
            self.assertEqual(user_0.account_status, before_last_inserted_license.account_type)
            self.assertEqual(DocumentType.Basic.name, before_last_inserted_license.license_type)

        except Exception as e:
            self.fail(e)

    def test_does_not_fetch_validated_licenses(self):
        license_table = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Rejected.name, datetime.now(), 0)

        self.license_repo.licenses.append(license_table)

        try:
            licenses = self.get_licenses_to_validate.worker()["items"]
            self.assertEqual(len(licenses), self.license_repo_base_size)

        except Exception as e:
            self.fail(e)

    def test_raise_400_when_page_is_smaller_than_1(self):
        license_table = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 0)

        self.license_repo.licenses.append(license_table)

        try:
            with self.assertRaises(ValueError):
                self.get_licenses_to_validate.worker(0)

        except Exception as e:
            self.fail(e)

    def test_page_only_contains_30_elements(self):
        license_table = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 0)

        for i in range(100):
            self.license_repo.licenses.append(license_table)

        try:
            licenses = self.get_licenses_to_validate.worker(1)["items"]
            self.assertEqual(len(licenses), 30)

        except Exception as e:
            self.fail(e)

    def test_page2_sends_next_30_elements(self):
        license_table1 = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 0)
        license_table2 = LicenseTable(2, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 999)

        for i in range(30):
            self.license_repo.licenses.append(license_table1)
        for i in range(30):
            self.license_repo.licenses.append(license_table2)

        try:
            licenses = self.get_licenses_to_validate.worker(1)["items"]
            self.assertEqual(len(licenses), 30)
            self.assertEqual(1, licenses[self.license_repo_base_size].document_id)

            licenses = self.get_licenses_to_validate.worker(2)["items"]
            self.assertEqual(len(licenses), 30)
            self.assertEqual(2, licenses[self.license_repo_base_size].document_id)

        except Exception as e:
            self.fail(e)

    def test_gets_the_right_count(self):
        license_table1 = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 0)
        license_table2 = LicenseTable(2, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.now(), 999)

        for i in range(30):
            self.license_repo.licenses.append(license_table1)
        for i in range(30):
            self.license_repo.licenses.append(license_table2)

        try:
            nb_documents = self.get_licenses_to_validate.worker(1)["nb_documents"]
            self.assertEqual(nb_documents, 60 + self.license_repo_base_size)

            nb_documents = self.get_licenses_to_validate.worker(2)["nb_documents"]
            self.assertEqual(nb_documents, 60 + self.license_repo_base_size)

        except Exception as e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()
