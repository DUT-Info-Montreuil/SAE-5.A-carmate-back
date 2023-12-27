import unittest
from datetime import datetime, timedelta
from hashlib import sha512

from api.worker.carpooling.use_case import CreateCarpooling
from api.worker.user import AccountStatus
from database.exceptions import CheckViolation
from database.schemas import UserTable, TokenTable, DriverProfileTable, CarpoolingTable


class CreateCarpoolingTestCase(unittest.TestCase):
    def setUp(self):
        self.create_carpooling = CreateCarpooling()

        user_without_driver_profile = UserTable(999, "Test", "Test", "test@test.fr",
                                                sha512("pass".encode('utf-8')).digest(), AccountStatus.Teacher.name,
                                                datetime.now())
        user_with_driver_profile = UserTable(1000, "Testo", "Testo", "testo@test.fr",
                                             sha512("pass".encode('utf-8')).digest(), AccountStatus.Teacher.name,
                                             datetime.now())
        token_without_driver_profile = TokenTable(sha512("user_without_driver_profile".encode()).digest(),
                                                  datetime.now() + timedelta(days=1), 999)
        token_with_driver_profile = TokenTable(sha512("user_with_driver_profile".encode()).digest(),
                                               datetime.now() + timedelta(days=1), 1000)
        driver_profile = DriverProfileTable(1500, "no desc", datetime.now(), 1000)

        self.create_carpooling.user_repository.users.append(user_with_driver_profile)
        self.create_carpooling.user_repository.users.append(user_without_driver_profile)
        self.create_carpooling.token_repository.tokens.append(token_with_driver_profile)
        self.create_carpooling.token_repository.tokens.append(token_without_driver_profile)
        self.create_carpooling.driver_profile_repository.driver_profiles.append(driver_profile)


    def test_fails_if_starting_point_bounds_invalid(self):
        with self.assertRaises(CheckViolation):
            self.create_carpooling.worker("user_with_driver_profile", [99, 2.36329], [48.85458, 2.1296], 3, 1,
                                          1732611600)

    def test_fails_if_destination_bounds_invalid(self):
        with self.assertRaises(CheckViolation):
            self.create_carpooling.worker("user_with_driver_profile", [48.85598, 2.36329], [99, 2.1296], 3, 1,
                                          1732611600)

    def test_inserts_carpooling(self):
        self.create_carpooling.worker("user_with_driver_profile", [48.85598, 2.36329], [48.85458, 2.1296], 3, 1,
                                      1732611600)

        carpooling_found: CarpoolingTable | None = None
        for carpooling in self.create_carpooling.carpooling_repository.carpoolings:
            if carpooling.driver_id == 1500:
                carpooling_found = carpooling

        if carpooling_found is None:
            self.fail("No carpooling has been created")

        self.assertEqual(carpooling.destination, [48.85458, 2.1296])
        self.assertEqual(carpooling.starting_point, [48.85598, 2.36329])
        self.assertEqual(carpooling.max_passengers, 3)
        self.assertEqual(carpooling.price, 1)
        self.assertEqual(carpooling.departure_date_time, datetime.fromtimestamp(1732611600))