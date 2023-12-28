from datetime import datetime
from hashlib import sha512

from api.worker import Worker
from api.worker.auth.use_case import PassengerCode
from api.worker.carpooling.models import BookingCarpoolingDTO
from api.exceptions import (
    CarpoolingAlreadyBooked,
    CarpoolingAlreadyFull,
    CarpoolingBookedTooLate,
    CarpoolingCanceled,
    CarpoolingNotFound,
    CredentialInvalid,
    InternalServerError
)
from database.schemas import CarpoolingTable, UserTable
from database.exceptions import (
    InternalServer,
    NotFound,
    UniqueViolation
)


class BookingCarpooling(Worker):
    def worker(self,
               token: str,
               carpooling_id: int) -> BookingCarpoolingDTO:
        user: UserTable
        try:
            user = self.token_repository.get_user(sha512(token.encode()).digest())
        except NotFound:
            raise CredentialInvalid()
        except InternalServer as e:
            raise InternalServerError(str(e))
        
        carpooling: CarpoolingTable
        try:
            carpooling = self.carpooling_repository.get_from_id(carpooling_id)
        except NotFound:
            raise CarpoolingNotFound()
        except InternalServer as e:
            raise InternalServerError(str(e))
        if carpooling.is_canceled:
            raise CarpoolingCanceled()
        
        carpooling_seats_taken: int
        try:
            carpooling_seats_taken = self.booking_carpooling_repository.seats_taken(carpooling_id)
        except NotFound:
            carpooling_seats_taken = 0
        except InternalServer as e:
            raise InternalServerError(str(e))
        
        if carpooling_seats_taken >= carpooling.max_passengers:
            raise CarpoolingAlreadyFull()
        
        today_date = datetime.now()
        if today_date > carpooling.departure_date_time:
            raise CarpoolingBookedTooLate()

        passenger_code = PassengerCode().worker()
        try:
            self.booking_carpooling_repository.insert(user.id,
                                                      carpooling_id,
                                                      passenger_code)
        except UniqueViolation:
            raise CarpoolingAlreadyBooked()
        except Exception as e:
            raise InternalServerError(str(e))
        return BookingCarpoolingDTO(passenger_code)
