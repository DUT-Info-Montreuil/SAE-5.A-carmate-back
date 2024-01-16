from abc import ABC
from typing import List, Tuple

from api.worker.carpooling.models import ReviewDTO
from database.schemas import UserTable


class ReviewRepositoryInterface(ABC):
    def insert(self,
               review: ReviewDTO,
               passenger_id: int): ...

    def get_list_best_drivers_according_economic_driving_rating_criterion(self) -> List[Tuple[UserTable,
                                                                                        int,
                                                                                        float,
                                                                                        int,
                                                                                        int]]: ...

    def get_list_best_drivers_according_safe_driving_rating_criterion(self) -> List[Tuple[UserTable,
                                                                                        int,
                                                                                        float,
                                                                                        int,
                                                                                        int]]: ...

    def get_list_best_drivers_according_sociability_rating_criterion(self) -> List[Tuple[UserTable,
                                                                                        int,
                                                                                        float,
                                                                                        int,
                                                                                        int]]: ...

    def get_average_criterions_from_driver(self, driver_id) -> Tuple[int,
                                                                     float,
                                                                     float,
                                                                     float]: ...
