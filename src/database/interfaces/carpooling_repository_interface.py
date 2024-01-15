from abc import ABC
from datetime import datetime
from typing import List, Tuple

from api.worker.carpooling.models import CarpoolingForRecap
from database.schemas import CarpoolingTable, Weekday


class CarpoolingRepositoryInterface(ABC):
    def insert(self,
               driver_id: int,
               starting_point: List[float],
               destination: List[float],
               max_passengers: int,
               price: float,
               departure_date_time: int) -> int: ...

    def get_carpoolings_route(self,
                              start_lat: float,
                              start_lon: float,
                              end_lat: float,
                              end_lon: float,
                              departure_date_time: int,
                              page: int = 1,
                              per_page: int = 10) -> Tuple[int, List[CarpoolingForRecap]] | Tuple[int, List]: ...

    def get_from_id(self,
                    carpooling_id: int) -> CarpoolingTable: ...

    def get_last_carpooling_between(self,
                                    driver_id: int,
                                    user_id: int) -> CarpoolingTable: ...

    def has_carpooling_between_dates_at_hour(self,
                                             start_date: datetime.date,
                                             end_date: datetime.date,
                                             at_time: datetime.time,
                                             on_days: List[Weekday],
                                             driver_id: int) -> bool: ...

    def has_carpooling_at(self,
                          driver_id: int,
                          timestamp: int) -> bool: ...
    
    def get_carpooling_created_by(self,
                                  driver_id: int) -> List[CarpoolingTable]: ...
