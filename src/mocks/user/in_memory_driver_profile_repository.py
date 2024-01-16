from datetime import datetime
from typing import List, Tuple

from database.interfaces import DriverProfileRepositoryInterface, UserRepositoryInterface, ReviewRepositoryInterface
from database.exceptions import (
    NotFound,
    UniqueViolation
)
from database.schemas import (
    DriverProfileTable,
    UserTable,
    ReviewTable
)


class InMemoryDriverProfileRepository(DriverProfileRepositoryInterface):
    user_repository: UserRepositoryInterface
    review_repository: ReviewRepositoryInterface

    def __init__(self,
                 user_repository: UserRepositoryInterface):
        self.user_repository = user_repository 
        self.review_repository: List[ReviewTable] = [
            ReviewTable(1, 1, 3.5, 4.2, 3.3, "Bonne ambiance", datetime.now(), datetime.now()),
            ReviewTable(3, 1, 2.71, 2.24, 1.8, "Bonne ambiance", datetime.now(), datetime.now()),
            ReviewTable(2, 1, 2.51, 3.24, 4.29, "Bonne ambiance", datetime.now(), datetime.now()),
            ReviewTable(4, 1, 0.4, 1.13, 2, "Bonne ambiance", datetime.now(), datetime.now()),
            ReviewTable(7, 1, 4.91, 4.73, 34.86, "Bonne ambiance", datetime.now(), datetime.now()),
        ]

        self.driver_profiles: List[DriverProfileTable] = [
            DriverProfileTable(0, 'Test of driver profile 1', datetime.now(), 4),
            DriverProfileTable(1, 'Test of driver profile 1', datetime.now(), 5),
            DriverProfileTable(2, 'Test of driver profile 1', datetime.now(), 6),

        ]
        self.driver_profile_count = len(self.driver_profiles)

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

    def get_average_criterions_from_driver(self, 
                                           driver_id: int) -> Tuple[int,
                                                                    float,
                                                                    float,
                                                                    float] | None:
        average_criterions: Tuple[int, float, float, float] | None
        nb_ratings_for_one_driver = 0
        average_criterions=(driver_id, 0, 0, 0)
        for review in self.review_repository:
            if driver_id == review.driver_id:
                nb_ratings_for_one_driver += 1
                average_criterions[1]+=review.economic_driving_rating
                average_criterions[2]+=review.safe_driving_rating
                average_criterions[3]+=review.sociability_rating
        if nb_ratings_for_one_driver == 0:
            return driver_id, *average_criterions
        average_criterions[1]/=nb_ratings_for_one_driver
        average_criterions[2]/=nb_ratings_for_one_driver
        average_criterions[3]/=nb_ratings_for_one_driver
        return driver.id, *average_criterions