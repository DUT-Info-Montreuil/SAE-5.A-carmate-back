import unittest

from api.worker.admin import ValidationStatus
from api.worker.admin.use_case import ValidateLicense
from api.exceptions import InvalidValidationStatus, LicenseNotFound
from mock.user import InMemoryLicenseRepository, InMemoryUserRepository


class ValidateLicenseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.user_repository = InMemoryUserRepository()
        self.license_repository = InMemoryLicenseRepository(self.user_repository)
        self.validate_license = ValidateLicense(self.license_repository, self.user_repository)

    def test_regular_usage(self):
        supposed_next_document_id: int | None = None

        self.validate_license.worker(1, ValidationStatus.Approved.name)

        supposed_next_document_id = self.get_next_document_to_validate().id

        if supposed_next_document_id is None:
            self.fail("test won't run work since there are no next document to validate")

        self.assertEqual(supposed_next_document_id, self.license_repository.get_next_license_id_to_validate())

    def test_next_document(self):
        self.assertIsNotNone(self.validate_license.worker(1, ValidationStatus.Approved.name))

    def test_wrong_license_id(self):
        with self.assertRaises(LicenseNotFound):
            self.validate_license.worker(65458, ValidationStatus.Rejected.name)

    def test_wrong_string(self):
        with self.assertRaises(InvalidValidationStatus):
            self.validate_license.worker(1, 'Dummy')

    def get_next_document_to_validate(self):
        for doc in self.license_repository.licenses:
            if doc.validation_status == ValidationStatus.Pending.name:
                return doc


if __name__ == '__main__':
    unittest.main()
