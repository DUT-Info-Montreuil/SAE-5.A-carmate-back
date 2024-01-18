import datetime

from hashlib import sha512
from typing import List

from api.exceptions import PassengerNotFound, ScheduledCarpoolingCannotBeCreated
from api.worker import Worker
from database.exceptions import NotFound
from database.schemas import (
    PassengerProfileTable,
    DriverProfileTable,
    PassengerScheduledCarpoolingTable,
    Weekday
)


class CreatePassengerScheduledCarpooling(Worker):
    def worker(self,
               label: str,
               starting_point: List[float],
               destination: List[float],
               start_date: datetime.date,
               end_date: datetime.date,
               start_hour: datetime.time,
               days: List[Weekday],
               token: str):

        passenger_profile: PassengerProfileTable
        try:
            passenger_profile = self.token_repository.get_passenger_profile(sha512(token.encode()).digest())
        except NotFound:
            raise PassengerNotFound()


        is_not_allowed_to_create = self.booking_carpooling_repository.has_reserved_carpooling_between_dates_at_hour(start_date,
                                                                                                                    end_date,
                                                                                                                    start_hour,
                                                                                                                    days,
                                                                                                                    passenger_profile.user_id)

        if is_not_allowed_to_create:
            raise ScheduledCarpoolingCannotBeCreated()

        is_not_allowed_to_create = self.propose_scheduled_carpooling_repository.has_same_time_proposed_scheduled_carpooling(start_date,
                                                                                                                            end_date,
                                                                                                                            days,
                                                                                                                            start_hour,
                                                                                                                            passenger_profile.id)

        if is_not_allowed_to_create:
            raise ScheduledCarpoolingCannotBeCreated()

        driver_profile: DriverProfileTable | None
        try:
            driver_profile = self.token_repository.get_driver_profile(sha512(token.encode()).digest())
        except NotFound:
            driver_profile = None

        if driver_profile is not None:
            is_not_allowed_to_create = self.carpooling_repository.has_carpooling_between_dates_at_hour(start_date,
                                                                                                       end_date,
                                                                                                       start_hour,
                                                                                                       days,
                                                                                                       driver_profile.id)
            if is_not_allowed_to_create:
                raise ScheduledCarpoolingCannotBeCreated()

            is_not_allowed_to_create = self.scheduled_carpooling_repository.has_same_time_scheduled_carpooling(start_date,
                                                                                                                end_date,
                                                                                                                days,
                                                                                                                start_hour,
                                                                                                                driver_profile.id)

            if is_not_allowed_to_create:
                raise ScheduledCarpoolingCannotBeCreated()


        return self.propose_scheduled_carpooling_repository.insert(label,
                                                                   starting_point,
                                                                   destination,
                                                                   start_date,
                                                                   end_date,
                                                                   start_hour,
                                                                   days,
                                                                   passenger_profile.id)
