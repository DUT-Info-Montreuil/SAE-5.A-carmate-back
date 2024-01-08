from psycopg2 import errorcodes
from psycopg2.errors import lookup

from api.worker.carpooling.models import ReviewDTO
from database import REVIEW_TABLE_NAME, establishing_connection
from database.interfaces import ReviewRepositoryInterface
from database.exceptions import UniqueViolation, InternalServer


class ReviewRepository(ReviewRepositoryInterface):
    def insert(self, review: ReviewDTO, passenger_id: int):
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
