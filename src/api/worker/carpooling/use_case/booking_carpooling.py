from datetime import datetime
from hashlib import sha512

from api.worker import Worker
from api.worker.carpooling.models import BookingCarpoolingDTO
from api.exceptions import (
    CarpoolingAlreadyBooked,
    CarpoolingAlreadyFull,
    CarpoolingBookedTooLate,
    CarpoolingCanceled,
    CarpoolingNotFound,
    CredentialInvalid,
    InternalServerError,
    BookingCanNotBeCreated
)
from database.schemas import (
    CarpoolingTable,
    PassengerProfileTable,
    Weekday,
    DriverProfileTable
)
from database.exceptions import (
    InternalServer,
    NotFound,
    UniqueViolation
)
from services import PassengerCodeService


class BookingCarpooling(Worker):
    def worker(self,
               token: str,
               carpooling_id: int) -> BookingCarpoolingDTO:
        passenger_profile: PassengerProfileTable
        driver_profile: DriverProfileTable
        try:
            passenger_profile = self.token_repository.get_passenger_profile(sha512(token.encode()).digest())
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
        try:
            driver_profile = self.token_repository.get_driver_profile(sha512(token.encode()).digest())
        except Exception:
            driver_profile = None

        if driver_profile:
            has_conflicts = self.carpooling_repository.has_carpooling_at(driver_profile.id,
                                                                         int(carpooling.departure_date_time.timestamp()))
            if has_conflicts:
                raise BookingCanNotBeCreated()

        has_conflicts = self.propose_scheduled_carpooling_repository.has_scheduled_with_date_and_day(passenger_profile.id,
                                                                                                     carpooling.departure_date_time.date(),
                                                                                                     Weekday(carpooling.departure_date_time.weekday() + 1))
        if has_conflicts:
            raise BookingCanNotBeCreated()

        has_conflicts = self.booking_carpooling_repository.has_reserved_carpooling_at(passenger_profile.user_id,
                                                                                      int(carpooling.departure_date_time.timestamp()))
        if has_conflicts:
            raise BookingCanNotBeCreated()

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

        passenger_code = PassengerCodeService.next()
        try:
            self.booking_carpooling_repository.insert(passenger_profile.user_id,
                                                      carpooling_id,
                                                      passenger_code)
        except UniqueViolation:
            raise CarpoolingAlreadyBooked()
        except Exception as e:
            raise InternalServerError(str(e))
        return BookingCarpoolingDTO(passenger_code)
