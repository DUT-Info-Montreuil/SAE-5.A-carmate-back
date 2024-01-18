from datetime import datetime, timedelta
from hashlib import sha512

from api.exceptions import (
    CarpoolingNotFound,
    DriverNotFound,
    CarpoolingNotFromThisDriver,
    InvalidTimeToConfirmCode,
    BookingNotFound,
    CarpoolingCanceled
)
from api.worker import Worker
from database.exceptions import NotFound
from database.schemas import CarpoolingTable, DriverProfileTable, ReserveCarpoolingTable


class ConfirmPassengerCode(Worker):
    def worker(self,
               carpooling_id: int,
               passenger_code: int,
               token: str):
        carpooling: CarpoolingTable
        driver: DriverProfileTable
        try:
            carpooling = self.carpooling_repository.get_from_id(carpooling_id)
        except NotFound:
            raise CarpoolingNotFound()

        if carpooling.is_canceled:
            raise CarpoolingCanceled()

        try:
            driver = self.token_repository.get_driver_profile(sha512(token.encode()).digest())
        except NotFound:
            raise DriverNotFound()

        if carpooling.driver_id != driver.id:
            raise CarpoolingNotFromThisDriver()

        now = datetime.now()
        if abs(carpooling.departure_date_time - now) > timedelta(hours=1):
            raise InvalidTimeToConfirmCode()

        reservation: ReserveCarpoolingTable
        try:
            reservation = self.booking_carpooling_repository.get_reservation_non_cancelled_by_carpooling_and_code(carpooling_id, passenger_code)
        except NotFound:
            raise BookingNotFound()

        self.booking_carpooling_repository.confirm_reservation(reservation.user_id, reservation.carpooling_id)

