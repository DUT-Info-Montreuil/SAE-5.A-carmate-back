from abc import ABC
from typing import List, Tuple

from api.worker.carpooling.models import CarpoolingForRecap
from database.schemas import CarpoolingTable


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
