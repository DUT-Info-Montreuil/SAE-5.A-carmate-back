from datetime import datetime
from hashlib import sha512
from typing import List

from api.exceptions import DriverNotFound, PassengerNotFound, ScheduledCarpoolingCannotBeCreated
from api.worker import Worker
from database.exceptions import NotFound
from database.schemas import Weekday, DriverProfileTable, PassengerProfileTable


class CreateDriverScheduledCarpooling(Worker):
    def worker(self,
               label: str,
               starting_point: List[float],
               destination: List[float],
               start_date: datetime.date,
               end_date: datetime.date,
               start_hour: datetime.time,
               days: List[Weekday],
               max_passengers: int,
               token: str):

        driver_profile: DriverProfileTable
        passenger_profile: PassengerProfileTable
        try:
            driver_profile = self.token_repository.get_driver_profile(sha512(token.encode()).digest())
        except NotFound:
            raise DriverNotFound()

        try:
            passenger_profile = self.token_repository.get_passenger_profile(sha512(token.encode()).digest())
        except NotFound:
            passenger_profile = None


        has_conflicts = self.booking_carpooling_repository.has_reserved_carpooling_between_dates_at_hour(start_date,
                                                                                                         end_date,
                                                                                                         start_hour,
                                                                                                         days,
                                                                                                         driver_profile.user_id)
        if has_conflicts:
            raise ScheduledCarpoolingCannotBeCreated()

        if passenger_profile:
            has_conflicts = self.propose_scheduled_carpooling_repository.has_same_time_proposed_scheduled_carpooling(start_date,
                                                                                                                     end_date,
                                                                                                                     days,
                                                                                                                     start_hour,
                                                                                                                     passenger_profile.id)
            if has_conflicts:
                raise ScheduledCarpoolingCannotBeCreated()

        has_conflicts = self.carpooling_repository.has_carpooling_between_dates_at_hour(start_date,
                                                                                        end_date,
                                                                                        start_hour,
                                                                                        days,
                                                                                        driver_profile.user_id)

        if has_conflicts:
            raise ScheduledCarpoolingCannotBeCreated()

        has_conflicts = self.scheduled_carpooling_repository.has_same_time_scheduled_carpooling(start_date,
                                                                                                 end_date,
                                                                                                 days,
                                                                                                 start_hour,
                                                                                                 driver_profile.id)
        if has_conflicts:
            raise ScheduledCarpoolingCannotBeCreated()

        return self.scheduled_carpooling_repository.insert(label,
                                                           starting_point,
                                                           destination,
                                                           start_date,
                                                           end_date,
                                                           start_hour,
                                                           days,
                                                           max_passengers,
                                                           driver_profile.id)
