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
        self.validate_license.worker(1, ValidationStatus.Approved.name)
        self.assertEqual(self.license_repository.get(1).validation_status, ValidationStatus.Approved.name)

    def test_next_document(self):
        self.assertIsNotNone(self.validate_license.worker(1, ValidationStatus.Approved.name))

    def test_wrong_license_id(self):
        with self.assertRaises(LicenseNotFound):
            self.validate_license.worker(65458, ValidationStatus.Rejected.name)

    def test_wrong_string(self):
        with self.assertRaises(InvalidValidationStatus):
            self.validate_license.worker(1, 'Dummy')


if __name__ == '__main__':
    unittest.main()