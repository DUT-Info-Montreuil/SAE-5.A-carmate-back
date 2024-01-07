from abc import ABC, abstractmethod
from typing import Tuple

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from database import BOOKING_CARPOOLING_TABLE_NAME, establishing_connection
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


class BookingCarpoolingRepository(BookingCarpoolingRepositoryInterface):
    def insert(self,
               user_id: int,
               carpooling_id: int,
               passenger_code: int) -> ReserveCarpoolingTable:
        query = f"""
            INSERT INTO carmate.{BOOKING_CARPOOLING_TABLE_NAME}(user_id, carpooling_id, passenger_code)
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
            FROM carmate.{BOOKING_CARPOOLING_TABLE_NAME}
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
