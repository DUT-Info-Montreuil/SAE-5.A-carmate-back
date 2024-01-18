from datetime import datetime
from typing import List, Tuple

from database.interfaces import (
    ReviewRepositoryInterface,
    UserRepositoryInterface,
    DriverProfileRepositoryInterface,
    CarpoolingRepositoryInterface,
    BookingCarpoolingRepositoryInterface
)
from database.schemas import ReviewTable, UserTable
from database.exceptions import NotFound, UniqueViolation


class InMemoryReviewRepository(ReviewRepositoryInterface):
    driver_profile_repository: DriverProfileRepositoryInterface
    user_repository: UserRepositoryInterface
    carpooling_repository: CarpoolingRepositoryInterface
    booking_carpooling_repository: BookingCarpoolingRepositoryInterface

    def __init__(self,
                 driver_profile_repository: DriverProfileRepositoryInterface,
                 user_repository: UserRepositoryInterface,
                 carpooling_repository: CarpoolingRepositoryInterface,
                 booking_carpooling_repository: BookingCarpoolingRepositoryInterface):
        self.driver_profile_repository = driver_profile_repository
        self.user_repository = user_repository
        self.carpooling_repository = carpooling_repository
        self.booking_carpooling_repository = booking_carpooling_repository

        self.reviews: List[ReviewTable] = [
            ReviewTable(0, 0, 2.5, 5, 2, ' ', datetime.now(), datetime.now()),
            ReviewTable(1, 0, 3, 4.5, 2, ' ', datetime.now(), datetime.now()),
            ReviewTable(2, 0, 1, 5, 2.5, ' ', datetime.now(), datetime.now()),
            ReviewTable(0, 1, 5, 1, 3, ' ', datetime.now(), datetime.now()),
            ReviewTable(1, 1, 4.5, 0.5, 1, ' ', datetime.now(), datetime.now()),
            ReviewTable(2, 1, 5, 2, 1, ' ', datetime.now(), datetime.now()),
            ReviewTable(0, 2, 1, 2.3, 5, ' ', datetime.now(), datetime.now()),
            ReviewTable(1, 2, 1, 1, 5, ' ', datetime.now(), datetime.now()),
            ReviewTable(2, 2, 0, 1.5, 5, ' ', datetime.now(), datetime.now())
        ]

    def insert(self, review, user_id: int):
        for r in self.reviews:
            if r.driver_id == r.driver_id \
                    and r.passenger_id == user_id:
                raise UniqueViolation("The review already exists")

        self.reviews.append(ReviewTable(
            user_id,
            review.driver_id,
            review.economic_driving_rating,
            review.safe_driving_rating,
            review.sociability_rating,
            review.review,
            datetime.now(),
            datetime.now()
        ))
    
    def __get_list_best_drivers_according_to_criterion_of(self, 
                                                          criterion: str) -> List[Tuple[UserTable,
                                                                                        int,
                                                                                        float,
                                                                                        int,
                                                                                        int]]:
        list_of_best_drivers: List[tuple] = []
        for driver_profile in self.driver_profile_repository.driver_profiles:
            user_table = next((user for user in self.user_repository.users if driver_profile.user_id == user.id), None)
            
            list_of_review_criterion_value = []
            nb_review_according_to_driver_id = 0
            for review in self.reviews:
                if review.driver_id == driver_profile.id:
                    list_of_review_criterion_value.append(getattr(review, criterion))
                    nb_review_according_to_driver_id += 1
            review_criterion_avg = sum(list_of_review_criterion_value)/nb_review_according_to_driver_id

            nb_carpooling_done = 0
            for carpooling in self.carpooling_repository.carpoolings:
                for booking_carpooling in self.booking_carpooling_repository.reserved_carpoolings:
                    if carpooling.id == booking_carpooling.carpooling_id \
                            and carpooling.driver_id == driver_profile.id:
                        nb_carpooling_done += 1
            list_of_best_drivers.append((
                user_table,
                driver_profile.id,
                review_criterion_avg,
                nb_review_according_to_driver_id,
                nb_carpooling_done
            ))
        return sorted(list_of_best_drivers, key=lambda x: x[2], reverse=True)[:10]

    def get_list_best_drivers_according_economic_driving_rating_criterion(self) -> List[Tuple[UserTable,
                                                                                        int,
                                                                                        float,
                                                                                        int,
                                                                                        int]]:
        return self.__get_list_best_drivers_according_to_criterion_of("economic_driving_rating")

    def get_list_best_drivers_according_safe_driving_rating_criterion(self) -> List[Tuple[UserTable,
                                                                                        int,
                                                                                        float,
                                                                                        int,
                                                                                        int]]:
        return self.__get_list_best_drivers_according_to_criterion_of("safe_driving_rating")

    def get_list_best_drivers_according_sociability_rating_criterion(self) -> List[Tuple[UserTable,
                                                                                        int,
                                                                                        float,
                                                                                        int,
                                                                                        int]]:
        return self.__get_list_best_drivers_according_to_criterion_of("sociability_rating")

