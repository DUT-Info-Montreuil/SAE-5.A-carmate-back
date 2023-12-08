import io
import os
import datetime
import unittest

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
            UserTable.to_self(
                (2, "Fred", "Mercury", "ssa@example.com", sha512("password".encode('utf-8')).digest(),
                 AccountStatus.Teacher.name, None))
        )
        self.get_licenses_to_validate = GetLicensesToValidate(self.license_repo)

    def test_successful_fetch_student_license(self):
        license_table = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.datetime.now(), 1)
        self.license_repo.licenses.append(license_table)
        try:
            licenses = self.get_licenses_to_validate.worker()["items"]

            self.assertEqual(1 + self.license_repo_base_size , len(licenses))
            self.assertEqual(self.user_repo.users[0].first_name, licenses[0].first_name)
            self.assertEqual(self.user_repo.users[0].last_name, licenses[0].last_name)
            self.assertEqual(license_table.id, licenses[0].document_id)
            self.assertEqual(AccountStatus.Student.name, licenses[0].account_type)
            self.assertEqual(DocumentType.Basic.name, licenses[0].license_type)
        except Exception as e:
            self.fail(e)

    def test_successful_fetch_multiple_licenses(self):
        license_table1 = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.datetime.now(), 1)
        license_table2 = LicenseTable(2, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.datetime.now(), 2)

        self.license_repo.licenses.append(license_table1)
        self.license_repo.licenses.append(license_table2)

        try:
            licenses = self.get_licenses_to_validate.worker()["items"]

            self.assertEqual(len(licenses), 2 + self.license_repo_base_size)

            self.assertEqual(self.user_repo.users[0].first_name, licenses[0].first_name)
            self.assertEqual(self.user_repo.users[0].last_name, licenses[0].last_name)
            self.assertEqual(license_table1.id, licenses[0].document_id)
            self.assertEqual(AccountStatus.Student.name, licenses[0].account_type)
            self.assertEqual(DocumentType.Basic.name, licenses[0].license_type)

            self.assertEqual(self.user_repo.users[1].first_name, licenses[(self.license_repo_base_size-1) + 2].first_name)
            self.assertEqual(self.user_repo.users[1].last_name, licenses[(self.license_repo_base_size-1) + 2].last_name)
            self.assertEqual(license_table2.id, licenses[(self.license_repo_base_size-1) + 2].document_id)
            self.assertEqual(AccountStatus.Teacher.name, licenses[(self.license_repo_base_size-1) + 2].account_type)
            self.assertEqual(DocumentType.Basic.name, licenses[(self.license_repo_base_size-1) + 2].license_type)

        except Exception as e:
            self.fail(e)

    def test_does_not_fetch_validated_licenses(self):
        license_table = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Rejected.name, datetime.datetime.now(), 1)

        self.license_repo.licenses.append(license_table)

        try:
            licenses = self.get_licenses_to_validate.worker()["items"]
            self.assertEqual(len(licenses), self.license_repo_base_size )

        except Exception as e:
            self.fail(e)

    def test_raise_400_when_page_is_smaller_than_1(self):
        license_table = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.datetime.now(), 1)

        self.license_repo.licenses.append(license_table)

        try:
            with self.assertRaises(ValueError):
                self.get_licenses_to_validate.worker(0)

        except Exception as e:
            self.fail(e)

    def test_page_only_contains_30_elements(self):
        license_table = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.datetime.now(), 1)

        for i in range(100):
            self.license_repo.licenses.append(license_table)

        try:
            licenses = self.get_licenses_to_validate.worker(1)["items"]
            self.assertEqual(len(licenses), 30)

        except Exception as e:
            self.fail(e)

    def test_page2_sends_next_30_elements(self):
        license_table1 = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.datetime.now(), 1)
        license_table2 = LicenseTable(2, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.datetime.now(), 2)

        for i in range(30):
            self.license_repo.licenses.append(license_table1)
        for i in range(30):
            self.license_repo.licenses.append(license_table2)

        try:
            licenses = self.get_licenses_to_validate.worker(1)["items"]
            self.assertEqual(len(licenses), 30)
            self.assertEqual(1, licenses[self.license_repo_base_size ].document_id)

            licenses = self.get_licenses_to_validate.worker(2)["items"]
            self.assertEqual(len(licenses), 30)
            self.assertEqual(2, licenses[self.license_repo_base_size].document_id)

        except Exception as e:
            self.fail(e)

    def test_gets_the_right_count(self):
        license_table1 = LicenseTable(1, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.datetime.now(), 1)
        license_table2 = LicenseTable(2, self.license_img, DocumentType.Basic.name, ValidationStatus.Pending.name, datetime.datetime.now(), 2)

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
