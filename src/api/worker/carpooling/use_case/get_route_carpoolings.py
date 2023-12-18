from typing import List, Tuple

from api.exceptions import InternalServerError
from api.worker.carpooling.models import CarpoolingForRecap
from database.repositories import CarpoolingRepositoryInterface
from database.schemas import CarpoolingTable


class GetRouteCarpoolings:
    carpooling_repository: CarpoolingRepositoryInterface

    def __init__(self,
                 carpooling_repository: CarpoolingRepositoryInterface) -> None:
        self.carpooling_repository = carpooling_repository

    def worker(self,
               start_lat: float,
               start_lon: float,
               end_lat: float,
               end_lon: float,
               departure_date_time: int,
               page: int | None = None) -> Tuple[int, List[CarpoolingForRecap]]:
        try:
            if page is not None:
                return self.carpooling_repository.get_carpoolings_route(start_lat, start_lon, end_lat, end_lon, departure_date_time,                                                                     page=page)
            else:
                return self.carpooling_repository.get_carpoolings_route(start_lat, start_lon, end_lat, end_lon, departure_date_time)
        except Exception as e:
            raise InternalServerError(str(e))
