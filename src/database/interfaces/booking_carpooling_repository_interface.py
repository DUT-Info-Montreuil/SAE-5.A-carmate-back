from abc import ABC
from datetime import datetime
from typing import List

from database.schemas import (
    PassengerProfileTable,
    ReserveCarpoolingTable,
    Weekday
)


class BookingCarpoolingRepositoryInterface(ABC):
    def insert(self,
               user_id: int,
               carpooling_id: int,
               passenger_code: int) -> ReserveCarpoolingTable: ...

    def seats_taken(self,
                    carpooling_id: int) -> int: ...

    def has_reserved_carpooling_between_dates_at_hour(self,
                                                      start_date: datetime.date,
                                                      end_date: datetime.date,
                                                      at_time: datetime.time,
                                                      on_days: List[Weekday],
                                                      user_id: int) -> bool: ...

    def get_reservation_non_cancelled_by_carpooling_and_code(self,
                                                             carpooling_id: int,
                                                             passenger_code: int) -> ReserveCarpoolingTable: ...

    def confirm_reservation(self,
                            user_id: int,
                            carpooling_id: int) -> None: ...

    def has_reserved_carpooling_at(self,
                                   user_id: int,
                                   timestamp: int): ...

    def get_passengers_from_carpooling(self,
                                       carpooling_id: int) -> List[PassengerProfileTable]: ...
    
    def get_booked_carpoolings(self,
                               user_id: int) -> List[ReserveCarpoolingTable]: ...
