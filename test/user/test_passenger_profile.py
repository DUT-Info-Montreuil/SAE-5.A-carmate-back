import unittest

from api.exceptions import (
    PassengerNotFound,
    ProfileAlreadyExist,
    UserNotFound
)
from api.worker.user.use_case import (
    CreatePassengerProfile,
    GetPassengerProfile
)


class PassengerProfileTestCase(unittest.TestCase):
    def setUp(self):
        self.create_passenger_profile = CreatePassengerProfile()
        self.get_passenger_profile = GetPassengerProfile()

        self.get_passenger_profile.passenger_profile_repository = self.create_passenger_profile.passenger_profile_repository

    def test_create_passenger_profile(self):
        try:
            passenger_profile_created = self.create_passenger_profile.worker("token-user-valid")
            self.assertIsNotNone(passenger_profile_created)
        except Exception as e:
            self.fail(e)
    
    def test_create_duplicate_passenger_profile(self):
        with self.assertRaises(ProfileAlreadyExist):
            self.create_passenger_profile.worker("token-user-valid")
            self.create_passenger_profile.worker("token-user-valid")

    def test_create_passenger_profile_with_invalid_token(self):
        with self.assertRaises(UserNotFound):
            self.create_passenger_profile.worker("token-invalid-user")

    def test_get_passenger_profile_with_passenger_id(self):
        try:
            passenger_profile_created = self.create_passenger_profile.worker("token-user-valid")
            self.get_passenger_profile.worker(passenger_id=passenger_profile_created)
        except Exception as e:
            self.fail(e)

    def test_get_passenger_profile_with_token(self):
        try:
            self.create_passenger_profile.worker("token-user-valid")
            self.get_passenger_profile.worker(token="token-user-valid")
        except Exception as e:
            self.fail(e)

    def test_get_passenger_profile_with_invalid_passenger_id(self):
        with self.assertRaises(PassengerNotFound):
            self.get_passenger_profile.worker(passenger_id=-1)

    def test_get_passenger_profile_with_invalid_token(self):
        with self.assertRaises(PassengerNotFound):
            self.get_passenger_profile.worker(token="token-invalid-user")


if __name__ == '__main__':
    unittest.main()
