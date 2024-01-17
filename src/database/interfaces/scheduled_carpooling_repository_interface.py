from abc import ABC
from datetime import datetime
from typing import List

from database.schemas import Weekday, DriverScheduledCarpoolingTable


class ScheduledCarpoolingRepositoryInterface(ABC):
    def has_same_time_scheduled_carpooling(self,
                                           start_date: datetime.date,
                                           end_date: datetime.date,
                                           days: List[Weekday],
                                           start_hour: datetime.time,
                                           driver_id: int) -> bool: ...

    def insert(self,
               label: str,
               starting_point: List[float],
               destination: List[float],
               start_date: datetime.date,
               end_date: datetime.date,
               start_hour: datetime.time,
               days: List[Weekday],
               max_passengers: int,
               driver_id: int) -> int: ...

    def get_passengers_for_schedule_carpooling(self, schedule_carpooling_id: int) -> List[tuple[int, datetime]]: ...

    def get_scheduled_carpooling(self, scheduled_carpooling_id: int) -> DriverScheduledCarpoolingTable: ...

    def has_scheduled_with_date_and_day(self,
                                        driver_id: int,
                                        date: datetime.date,
                                        day: Weekday) -> bool: ...
