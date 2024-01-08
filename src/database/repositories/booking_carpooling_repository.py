from abc import ABC, abstractmethod
from typing import Tuple, List

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from api.worker.user.models import FutureReservationDTO
from database import establishing_connection
from database.repositories import booking_carpooling_table_name, carpooling_table_name
from database.schemas import ReserveCarpoolingTable
from database.exceptions import InternalServer, NotFound, UniqueViolation


class BookingCarpoolingRepositoryInterface(ABC):
    @abstractmethod
    def insert(self,
               user_id: int,
               carpooling_id: int,
               passenger_code: int) -> ReserveCarpoolingTable: ...

    def seats_taken(self,
                   carpooling_id: int) -> int: ...

    def get_future_reservations_by_passenger_id(self,
                                                user_id: int) -> List[FutureReservationDTO]: ...

class BookingCarpoolingRepository(BookingCarpoolingRepositoryInterface):
    def insert(self,
               user_id: int,
               carpooling_id: int,
               passenger_code: int) -> ReserveCarpoolingTable:
        query = f"""
            INSERT INTO carmate.{booking_carpooling_table_name}(user_id, carpooling_id, passenger_code)
            VALUES (%s, %s, %s)
            RETURNING user_id, carpooling_id, passenger_code
        """

        booking_carpooling: Tuple[int, int, int]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user_id, carpooling_id, passenger_code,))
                except lookup(errorcodes.UNIQUE_VIOLATION):
                    raise UniqueViolation("carpooling already taken")
                except Exception as e:
                    raise InternalServer(str(e))
                booking_carpooling = curs.fetchone()
        return ReserveCarpoolingTable(*booking_carpooling)

    def seats_taken(self,
                   carpooling_id: int) -> int:
        query = f"""
            SELECT count(user_id)
            FROM carmate.{booking_carpooling_table_name}
            WHERE carpooling_id=%s
        """

        carpooling_seats_taken: Tuple[int]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (carpooling_id,))
                except ProgrammingError:
                    raise NotFound(f"no booking for {carpooling_id}")
                except Exception as e:
                    raise InternalServer(str(e))
                carpooling_seats_taken = curs.fetchone()

        if carpooling_seats_taken is None:
            raise NotFound(f"no booking for {carpooling_id}")
        return carpooling_seats_taken[0]

    def get_future_reservations_by_passenger_id(self,
                                                user_id: int) -> List[FutureReservationDTO]:
        query = f"""
            SELECT rc.passenger_code, c.driver_id, c.departure_date_time, c.destination, c.starting_point, c.id
            FROM carmate.{booking_carpooling_table_name} rc
            INNER JOIN carmate.{carpooling_table_name} c 
                ON c.id = rc.carpooling_id
            WHERE rc.user_id=%s 
                AND rc.canceled='f' 
                AND c.is_canceled='f' 
                AND c.departure_date_time > NOW()
        """
        future_reservations: List[Tuple]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user_id,))
                except Exception as e:
                    raise InternalServer(str(e))
                future_reservations = curs.fetchall()

        return [FutureReservationDTO(*future_reservation) for future_reservation in future_reservations]
