from datetime import datetime
from typing import List

from api.worker.user.models import FutureReservationDTO
from database.repositories import BookingCarpoolingRepositoryInterface
from database.schemas import ReserveCarpoolingTable
from database.exceptions import UniqueViolation


class InMemoryBookingCarpoolingRepository(BookingCarpoolingRepositoryInterface):    
    def __init__(self, carpooling_repository=None) -> None:
        self.reserved_carpoolings: List[ReserveCarpoolingTable] = [
            ReserveCarpoolingTable(1, 1, 123456),
            ReserveCarpoolingTable(2, 1, 123456),
            ReserveCarpoolingTable(3, 1, 123456),
            ReserveCarpoolingTable(4, 1, 123456)
        ]
        self.carpooling_repository = carpooling_repository

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

    def get_future_reservations_by_passenger_id(self,
                                                user_id: int) -> List[FutureReservationDTO]:
        reservations: List[ReserveCarpoolingTable] = []
        for reservation in self.reserved_carpoolings:
            if reservation.user_id == user_id \
                    and reservation.canceled is False:
                reservations.append(reservation)

        future_reservations: List[FutureReservationDTO] = []
        for reservation in reservations:
            for carpooling in self.carpooling_repository.carpoolings:
                if carpooling.id == reservation.carpooling_id \
                        and carpooling.is_canceled is False \
                        and carpooling.departure_date_time > datetime.now():
                    future_reservations.append(
                        FutureReservationDTO(reservation.passenger_code,
                                             carpooling.driver_id,
                                             carpooling.departure_date_time,
                                             carpooling.destination,
                                             carpooling.starting_point,
                                             carpooling.id)
                    )

        return future_reservations
