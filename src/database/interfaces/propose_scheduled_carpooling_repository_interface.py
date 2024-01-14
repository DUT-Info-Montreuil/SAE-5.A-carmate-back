from abc import ABC
from datetime import datetime
from typing import List

from database.schemas import CarpoolingTable, Weekday


class ProposeScheduledCarpoolingRepositoryInterface(ABC):
    def insert(self,
               label: str,
               starting_point: List[float],
               destination: List[float],
               start_date: datetime.date,
               end_date: datetime.date,
               start_hour: datetime.time,
               days: List[Weekday],
               passenger_id: int) -> int: ...

    def has_same_time_proposed_scheduled_carpooling(self,
                                                    start_date: datetime.date,
                                                    end_date: datetime.date,
                                                    days: List[Weekday],
                                                    start_hour: datetime.time,
                                                    passenger_id: int) -> bool: ...

    def get_carpoolings_to_reserve_for(self, propose_scheduled_carpooling_id: int) -> List[CarpoolingTable]: ...

    def get_user_id_from_scheduled_carpooling(self, propose_scheduled_carpooling_id: int) -> int: ...

    def get_matching_proposed_scheduled_carpooling(self,
                                                   starting_point: List[float],
                                                   destination: List[float],
                                                   date: datetime.date,
                                                   time: datetime.time,
                                                   limit: int) -> List[int]: ...

    def has_scheduled_with_date_and_day(self,
                                        passenger_id: int,
                                        date: datetime.date,
                                        day: Weekday) -> bool: ...

    def get_carpoolings_to_create_and_reserve_for(self, propose_scheduled_carpooling_id: int) -> List[tuple[int, datetime, int, List[float], List[float]]]: ...
