from abc import ABC

from database.schemas import ReserveCarpoolingTable


class BookingCarpoolingRepositoryInterface(ABC):
    def insert(self,
               user_id: int,
               carpooling_id: int,
               passenger_code: int) -> ReserveCarpoolingTable: ...

    def seats_taken(self,
                    carpooling_id: int) -> int: ...
