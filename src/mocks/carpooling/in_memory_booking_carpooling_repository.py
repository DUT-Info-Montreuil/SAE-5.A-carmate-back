from typing import List

from database.repositories import BookingCarpoolingRepositoryInterface
from database.schemas import ReserveCarpoolingTable
from database.exceptions import UniqueViolation


class InMemoryBookingCarpoolingRepository(BookingCarpoolingRepositoryInterface):    
    def __init__(self) -> None:
        self.reserved_carpoolings: List[ReserveCarpoolingTable] = [
            ReserveCarpoolingTable(1, 1, 123456),
            ReserveCarpoolingTable(2, 1, 123456),
            ReserveCarpoolingTable(3, 1, 123456),
            ReserveCarpoolingTable(4, 1, 123456)
        ]

    def insert(self,
               user_id: int,
               carpooling_id: int,
               passenger_code: int) -> ReserveCarpoolingTable:
        if any(reservation.carpooling_id == carpooling_id for reservation in self.reserved_carpoolings):
            raise UniqueViolation("carpooling already taken")

        reservation = ReserveCarpoolingTable(user_id, carpooling_id, passenger_code)
        self.reserved_carpoolings.append(reservation)
        return reservation

    def seats_taken(self, carpooling_id: int) -> int:
        return sum(1 for reservation in self.reserved_carpoolings if reservation.carpooling_id == carpooling_id)
