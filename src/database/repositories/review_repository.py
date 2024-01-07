from abc import ABC
from typing import List, Tuple

from psycopg2 import errorcodes
from psycopg2.errors import lookup

from api.worker.carpooling.models import ReviewDTO
from database import establishing_connection
from database.repositories import DriverProfileRepository, UserRepository
from database.exceptions import UniqueViolation, InternalServer
from database.schemas import ReviewTable, UserTable


class ReviewRepositoryInterface(ABC):
    def insert(self,
               review: ReviewDTO, 
               passenger_id: int): ...

    def get_list_best_drivers_according_economic_driving_rating_criterion(self) -> List[Tuple[UserTable, int, float]]: ...

    def get_list_best_drivers_according_safe_driving_rating_criterion(self) -> List[Tuple[UserTable, int, float]]: ...
    
    def get_list_best_drivers_according_sociability_rating_criterion(self) -> List[Tuple[UserTable, int, float]]: ...



class ReviewRepository(ReviewRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "review"
    MAX_BEST_DRIVERS_REVIEW_LISTING: int = 10
    
    def insert(self, review: ReviewDTO, passenger_id: int):
        query = f"""
                INSERT INTO {self.POSTGRES_TABLE_NAME}(passenger_id, 
                                                       driver_id, 
                                                       economic_driving_rating, 
                                                       safe_driving_rating, 
                                                       sociability_rating, 
                                                       review) 
                VALUES (%s, %s, %s, %s, %s, %s)
        """

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (passenger_id,
                                         review.driver_id,
                                         review.economic_driving_rating,
                                         review.safe_driving_rating,
                                         review.sociability_rating,
                                         review.review))
                except lookup(errorcodes.UNIQUE_VIOLATION):
                    raise UniqueViolation("The review already exists")
                except Exception as e:
                    raise InternalServer(str(e))
    
    def __get_list_best_drivers_according_to_criterion_of(self, 
                                                          criterion: str) -> List[Tuple[UserTable, int, float]]:
        query = f"""
            SELECT u.*,
                dp.id,
                {criterion}_avg.avg
            FROM carmate.{DriverProfileRepository.POSTGRES_TABLE_NAME} dp
            INNER JOIN carmate.{UserRepository.POSTGRES_TABLE_NAME} u
                ON dp.user_id = u.id
            LEFT JOIN (
                SELECT r.driver_id, AVG(r.{criterion}) AS avg
                FROM carmate.{ReviewRepository.POSTGRES_TABLE_NAME} r
                GROUP BY r.driver_id
            ) {criterion}_avg
                ON dp.id = {criterion}_avg.driver_id
            ORDER BY {criterion}_avg.avg DESC
            LIMIT {ReviewRepository.MAX_BEST_DRIVERS_REVIEW_LISTING};
        """

        list_best_drivers: list
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query)
                except Exception as e:
                    raise InternalServer(str(e))
                list_best_drivers = curs.fetchall()

        nb_fields_user_table =len(UserTable.__annotations__.items())
        return [
            (UserTable(*row[:nb_fields_user_table]), row[nb_fields_user_table], row[-1])
            for row in list_best_drivers
        ]
    
    def get_list_best_drivers_according_economic_driving_rating_criterion(self) -> List[Tuple[UserTable, int, float]]:
        return self.__get_list_best_drivers_according_to_criterion_of("economic_driving_rating")

    def get_list_best_drivers_according_safe_driving_rating_criterion(self) -> List[Tuple[UserTable, int, float]]:
        return self.__get_list_best_drivers_according_to_criterion_of("safe_driving_rating")

    def get_list_best_drivers_according_sociability_rating_criterion(self) -> List[Tuple[UserTable, int, float]]:
        return self.__get_list_best_drivers_according_to_criterion_of("sociability_rating")
