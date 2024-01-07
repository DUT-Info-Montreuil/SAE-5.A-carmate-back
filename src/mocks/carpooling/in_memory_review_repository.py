from datetime import datetime
from typing import List, Tuple

from database.repositories import (
    ReviewRepositoryInterface,
    UserRepositoryInterface,
    PassengerProfileRepositoryInterface
)
from database.schemas import ReviewTable, UserTable
from database.exceptions import NotFound, UniqueViolation


class InMemoryReviewRepository(ReviewRepositoryInterface):
    user_repository: UserRepositoryInterface
    passenger_profile_repository: PassengerProfileRepositoryInterface

    def __init__(self,
                 passenger_profile_repository: PassengerProfileRepositoryInterface,
                 user_repository: UserRepositoryInterface):
        self.passenger_profile_repository = passenger_profile_repository
        self.user_repository = user_repository

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
                                                          criterion: str) -> List[Tuple[UserTable, int, float]]:
        list_best_drivers = []
        for review in self.reviews:
            user_id: int = -1
            for passenger_profile in self.passenger_profile_repository.passenger_profiles:
                if passenger_profile.id == review.passenger_id:
                    user_id = passenger_profile.user_id
            
            if user_id < 0:
                raise NotFound("user not found")
            user_table: UserTable | None = None
            for user in self.user_repository.users:
                if user.id == user_id:
                    user_table = user
            
            if user_table is None:
                raise NotFound("user not found")
            list_best_drivers.append((user_table, review.driver_id, getattr(review, criterion)))

        list_best_drivers.sort(key=lambda x: x[-1], reverse=True)
        return list_best_drivers

    def get_list_best_drivers_according_economic_driving_rating_criterion(self) -> List[Tuple[UserTable, ReviewTable]]:
        return self.__get_list_best_drivers_according_to_criterion_of("economic_driving_rating")

    def get_list_best_drivers_according_safe_driving_rating_criterion(self) -> List[Tuple[UserTable, ReviewTable]]:
        return self.__get_list_best_drivers_according_to_criterion_of("safe_driving_rating")

    def get_list_best_drivers_according_sociability_rating_criterion(self) -> List[Tuple[UserTable, ReviewTable]]:
        return self.__get_list_best_drivers_according_to_criterion_of("sociability_rating")

