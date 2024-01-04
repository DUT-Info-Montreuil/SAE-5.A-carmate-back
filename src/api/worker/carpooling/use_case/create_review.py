from datetime import datetime, timedelta
from hashlib import sha512

from api.worker import Worker
from api.worker.carpooling.models import ReviewDTO
from api.exceptions import (
    CarpoolingNotFound,
    InternalServerError,
    CarpoolingReviewTimeExpired,
    PassengerNotFound
)
from database.schemas import CarpoolingTable, PassengerProfileTable
from database.exceptions import NotFound


class CreateReview(Worker):
    def worker(self, 
               review: ReviewDTO, 
               token: str) -> None:
        passenger: PassengerProfileTable
        try:
            passenger = self.token_repository.get_passenger_profile(sha512(token.encode()).digest())
        except NotFound:
            raise PassengerNotFound("passenger not found")
        except Exception as e:
            raise InternalServerError(str(e))

        last_carpooling: CarpoolingTable
        try:
            last_carpooling = self.carpooling_repository.get_last_carpooling_between(review.driver_id, passenger.user_id)
        except NotFound:
            raise CarpoolingNotFound()
        except Exception as e:
            raise InternalServerError(str(e))

        if last_carpooling.departure_date_time < datetime.now() - timedelta(weeks=1):
            raise CarpoolingReviewTimeExpired()

        self.review_repository.insert(review, passenger.id)

