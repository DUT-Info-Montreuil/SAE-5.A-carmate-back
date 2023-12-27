import io
import os
import unittest

from api.exceptions import (
    DriverNotFound,
    ProfileAlreadyExist,
    UserNotFound
)
from api.worker.user.use_case import (
    CreateDriverProfile,
    GetDriverProfile
)


class DriverProfileTestCase(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), "../res/driver-license.jpg"), "rb") as f:
            self.license_img = io.BytesIO(f.read())
        
        self.create_driver_profile = CreateDriverProfile()
        self.get_driver_profile = GetDriverProfile()
        self.get_driver_profile.driver_profile_repository = self.create_driver_profile.driver_profile_repository

    def test_create_driver_profile(self):
        try:
            driver_profile_created = self.create_driver_profile.worker("token-user-valid", self.license_img)
            self.assertIsNotNone(driver_profile_created)
        except Exception as e:
            self.fail(e)
    
    def test_create_duplicate_driver_profile(self):
        with self.assertRaises(ProfileAlreadyExist):
            self.create_driver_profile.worker("token-user-valid", self.license_img)
            self.create_driver_profile.worker("token-user-valid", self.license_img)

    def test_create_driver_profile_with_invalid_token(self):
        with self.assertRaises(UserNotFound):
            self.create_driver_profile.worker("token-invalid-user", self.license_img)

    def test_get_driver_profile_with_driver_id(self):
        try:
            driver_profile_created = self.create_driver_profile.worker("token-user-valid", self.license_img)
            self.assertIsNotNone(driver_profile_created)
            self.get_driver_profile.worker(driver_id=driver_profile_created.id)
        except Exception as e:
            self.fail(e)

    def test_get_driver_profile_with_token(self):
        try:
            self.create_driver_profile.worker("token-user-valid", self.license_img)
            self.get_driver_profile.worker(token="token-user-valid")
        except Exception as e:
            self.fail(e)

    def test_get_driver_profile_with_invalid_driver_id(self):
        with self.assertRaises(DriverNotFound):
            self.get_driver_profile.worker(driver_id=-1)

    def test_get_driver_profile_with_invalid_token(self):
        with self.assertRaises(DriverNotFound):
            self.get_driver_profile.worker(token="token-invalid-user")


if __name__ == '__main__':
    unittest.main()
