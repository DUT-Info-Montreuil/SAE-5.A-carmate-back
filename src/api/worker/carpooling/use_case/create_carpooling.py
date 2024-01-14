from datetime import datetime
from hashlib import sha512
from typing import List

from api.exceptions import CarpoolingCanNotBeCreated
from api.worker import Worker
from database.schemas import Weekday, PassengerProfileTable


class CreateCarpooling(Worker):
    def worker(self,
               token: str,
               starting_point: List[float],
               destination: List[float],
               max_passengers: int,
               price: float,
               departure_date_time: int) -> int:
        passenger: PassengerProfileTable
        driver = self.token_repository.get_driver_profile(sha512(token.encode()).digest())

        try:
            passenger = self.token_repository.get_passenger_profile(sha512(token.encode()).digest())
        except Exception:
            passenger = None

        has_conflicts = self.booking_carpooling_repository.has_reserved_carpooling_at(driver.user_id, departure_date_time)
        if has_conflicts:
            raise CarpoolingCanNotBeCreated()

        date_from_timestamp = datetime.fromtimestamp(departure_date_time)
        if passenger:
            has_conflicts = self.propose_scheduled_carpooling_repository.has_scheduled_with_date_and_day(passenger.id,
                                                                                                         date_from_timestamp.date(),
                                                                                                         Weekday(date_from_timestamp.weekday() + 1))
            if has_conflicts:
                raise CarpoolingCanNotBeCreated()

        has_conflicts = self.carpooling_repository.has_carpooling_at(driver.id, departure_date_time)
        if has_conflicts:
            raise CarpoolingCanNotBeCreated()

        has_conflicts = self.scheduled_carpooling_repository.has_scheduled_with_date_and_day(driver.id,
                                                                                             date_from_timestamp.date(),
                                                                                             Weekday(date_from_timestamp.weekday() + 1))

        if has_conflicts:
            raise CarpoolingCanNotBeCreated()

        return self.carpooling_repository.insert(driver.id, starting_point, destination, max_passengers, price, departure_date_time)
