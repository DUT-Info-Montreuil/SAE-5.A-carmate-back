from datetime import datetime
from typing import List, Tuple

from database.interfaces import DriverProfileRepositoryInterface, UserRepositoryInterface
from database.exceptions import (
    NotFound,
    UniqueViolation
)
from database.schemas import (
    DriverProfileTable,
    UserTable
)


class InMemoryDriverProfileRepository(DriverProfileRepositoryInterface):
    user_repository: UserRepositoryInterface

    def __init__(self,
                 user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

        self.driver_profile_count = 0
        self.driver_profiles: List[DriverProfileTable] = []

    def insert(self,
               user: UserTable) -> DriverProfileTable:
        for driver in self.driver_profiles:
            if driver.user_id == user.id:
                raise UniqueViolation("driver profile already exist")

        in_memory_driver_profile = DriverProfileTable(
            self.driver_profile_count, ' ', datetime.now(), user.id)

        self.driver_profiles.append(in_memory_driver_profile)
        self.driver_profile_count = self.driver_profile_count + 1
        return in_memory_driver_profile

    def get_driver_by_user_id(self,
                              user_id: int) -> Tuple[DriverProfileTable, 
                                                     bytes | None]:
        for driver in self.driver_profiles:
            if driver.user_id == user_id:
                profile_picture: bytes | None = self.user_repository.get_user_by_id(driver.user_id).profile_picture
                return driver, profile_picture
        raise NotFound("Driver not found")

    def get_driver(self,
                   driver_id: int) -> Tuple[DriverProfileTable, 
                                                     bytes | None]:
        for driver in self.driver_profiles:
            if driver.id == driver_id:
                profile_picture: bytes | None = self.user_repository.get_user_by_id(driver.user_id).profile_picture
                return driver, profile_picture
        raise NotFound("Driver not found")
