from datetime import datetime
from typing import List

from database.schemas import ReserveCarpoolingTable, CarpoolingTable, Weekday
from database.interfaces import BookingCarpoolingRepositoryInterface
from database.schemas import ReserveCarpoolingTable


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
        # totalement bullshit  c'est valide que si on a forcément max_passengers = 1 ...
        #if any(reservation.carpooling_id == carpooling_id for reservation in self.reserved_carpoolings):
        #    raise UniqueViolation("carpooling already taken")

        reservation = ReserveCarpoolingTable(user_id, carpooling_id, passenger_code)
        self.reserved_carpoolings.append(reservation)
        return reservation

    def seats_taken(self, carpooling_id: int) -> int:
        return sum(1 for reservation in self.reserved_carpoolings if reservation.carpooling_id == carpooling_id)

    def has_reserved_carpooling_between_dates_at_hour(self,
                                                      start_date: datetime.date,
                                                      end_date: datetime.date,
                                                      at_time: datetime.time,
                                                      on_days: List[Weekday],
                                                      user_id: int) -> bool:
        if self.carpooling_repository is None:
            raise Exception("this function won't work without carpooling repository")

        carpooling_ids: List[int] = []

        for reserved in self.reserved_carpoolings:
            if reserved.user_id == user_id \
                    and not reserved.canceled:
                carpooling_ids.append(reserved.carpooling_id)

        carpoolings = [carpooling for carpooling in self.carpooling_repository.carpoolings if carpooling.id in carpooling_ids]

        if len(carpoolings) != len(carpooling_ids):
            raise Exception("Incoherent data, some carpooling id does not matches any carpooling")

        for carpooling in carpoolings:
            if carpooling.is_canceled is False \
                    and start_date <= carpooling.departure_date_time.date() <= end_date \
                    and carpooling.departure_date_time.time() == at_time \
                    and Weekday(carpooling.departure_date_time.weekday() + 1) in on_days:
                return True

        return False