from typing import List, Tuple

from psycopg2 import errorcodes
from psycopg2.errors import lookup

from api.worker.carpooling.models import ReviewDTO
from database import (
    REVIEW_TABLE_NAME,
    DRIVER_PROFILE_TABLE_NAME,
    USER_TABLE_NAME,
    CARPOOLING_TABLE_NAME,
    BOOKING_CARPOOLING_TABLE_NAME,
    establishing_connection
)
from database.interfaces import ReviewRepositoryInterface
from database.exceptions import UniqueViolation, InternalServer
from database.schemas import UserTable


class ReviewRepository(ReviewRepositoryInterface):
    MAX_BEST_DRIVERS_REVIEW_LISTING: int = 10

    def insert(self,
               review: ReviewDTO,
               passenger_id: int):
        query = f"""
                INSERT INTO {REVIEW_TABLE_NAME}(passenger_id, 
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
                                                          criterion: str) -> List[Tuple[UserTable,
                                                                                        int,
                                                                                        float,
                                                                                        int,
                                                                                        int]]:
        query = f"""
            SELECT u.*,
                dp.id,
                {criterion}.avg,
                {criterion}.nb_review,
                nb_carpooling_done.value AS nb_carpooling_done
            FROM carmate.{DRIVER_PROFILE_TABLE_NAME} dp
            INNER JOIN carmate.{USER_TABLE_NAME} u
                ON dp.user_id = u.id
            LEFT JOIN (
                SELECT r.driver_id, 
                    AVG(r.{criterion}) AS avg,
                    COUNT(r.{criterion}) AS nb_review
                FROM carmate.{REVIEW_TABLE_NAME} r
                GROUP BY r.driver_id
            ) {criterion}
                ON dp.id = {criterion}.driver_id
            LEFT JOIN (
                SELECT c.driver_id,
                    COUNT(c.id) AS value
                FROM carmate.{CARPOOLING_TABLE_NAME} c
                INNER JOIN carmate.{BOOKING_CARPOOLING_TABLE_NAME} bc
                    ON c.id=bc.carpooling_id
                WHERE bc.passenger_code_validated=true 
                    AND bc.canceled=true
                GROUP BY c.driver_id
            ) nb_carpooling_done
                ON dp.id = nb_carpooling_done.driver_id
            ORDER BY {criterion}.avg DESC
            LIMIT {self.MAX_BEST_DRIVERS_REVIEW_LISTING}
        """

        list_best_drivers: list
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query)
                except Exception as e:
                    raise InternalServer(str(e))
                list_best_drivers = curs.fetchall()

        nb_fields_user_table = len(UserTable.__annotations__.items())
        return [
            (UserTable(*row[:nb_fields_user_table]),
             row[nb_fields_user_table],
             row[nb_fields_user_table + 1],
             row[nb_fields_user_table + 2],
             row[-1])
            for row in list_best_drivers
        ]

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
    
    def get_average_criterions_from_driver(self, driver_id) -> Tuple[int, 
                                                                     float,
                                                                     float,
                                                                     float] | None:
        query = f"""
            SELECT driver_id, 
                AVG(economic_driving_rating),
                AVG(safe_driving_rating),
                AVG(sociability_rating),
            FROM carmate.{REVIEW_TABLE_NAME}
            GROUP BY driver_id
        """

        average_criterions: list
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query)
                except Exception as e:
                    raise InternalServer(str(e))
                average_criterions = curs.fetchone()
        
        if average_criterions is None:
            return None
        return average_criterions[0:]

