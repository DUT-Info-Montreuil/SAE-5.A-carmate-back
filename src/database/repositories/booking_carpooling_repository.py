import datetime
from typing import Tuple, List

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from database import (
    BOOKING_CARPOOLING_TABLE_NAME,
    CARPOOLING_TABLE_NAME,
    PASSENGER_PROFILE_TABLE_NAME,
    establishing_connection
)
from database.interfaces import BookingCarpoolingRepositoryInterface
from database.exceptions import (
    InternalServer,
    NotFound,
    UniqueViolation
)
from database.schemas import (
    ReserveCarpoolingTable,
    PassengerProfileTable,
    Weekday
)


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

    def has_reserved_carpooling_between_dates_at_hour(self,
                                                      start_date: datetime.date,
                                                      end_date: datetime.date,
                                                      at_time: datetime.time,
                                                      on_days: List[Weekday],
                                                      user_id: int) -> bool:
        query = f"""
                SELECT EXISTS(
                        SELECT 1
                        FROM carmate.{BOOKING_CARPOOLING_TABLE_NAME} rc
                        INNER JOIN carmate.{CARPOOLING_TABLE_NAME} c 
                            ON (rc.carpooling_id = c.id)
                        WHERE rc.user_id = %s 
                            AND rc.canceled = 'f'
                            AND c.is_canceled = 'f'
                            AND EXTRACT(ISODOW FROM c.departure_date_time) = ANY(%s)
                            AND c.departure_date_time BETWEEN %s AND %s
                            AND c.departure_date_time::time = %s
                        LIMIT 1
                )
        """
        has_reserved_carpooling: bool = False
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user_id, [day.value for day in on_days], start_date, end_date, at_time))
                except Exception as e:
                    raise InternalServer(str(e))
                has_reserved_carpooling = curs.fetchone()[0]

        return has_reserved_carpooling

    def get_reservation_non_cancelled_by_carpooling_and_code(self,
                                                             carpooling_id: int,
                                                             passenger_code: int) -> ReserveCarpoolingTable:
        query = f"""
            SELECT *
            FROM carmate.{BOOKING_CARPOOLING_TABLE_NAME}
            WHERE carpooling_id = %s
                AND passenger_code = %s
                AND canceled = 'f'
                AND passenger_code_validated = 'f'
        """
        reservation: Tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (carpooling_id, passenger_code,))
                except Exception as e:
                    raise InternalServer(str(e))
                reservation = curs.fetchone()

        if reservation is None:
            raise NotFound(f"no reservation for carpooling_id {carpooling_id} and passenger_code {passenger_code}")
        return ReserveCarpoolingTable(*reservation)

    def confirm_reservation(self,
                            user_id: int,
                            carpooling_id: int) -> None:
        query = f"""
            UPDATE carmate.{BOOKING_CARPOOLING_TABLE_NAME}
            SET 
                passenger_code_validated = 't',
                passenger_code_date_validated = NOW()
            WHERE 
                user_id = %s
                AND carpooling_id = %s
                AND canceled = 'f'
                AND passenger_code_validated = 'f'
        """
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user_id, carpooling_id))
                except Exception as e:
                    raise InternalServer(str(e))

    def has_reserved_carpooling_at(self,
                                   user_id: int,
                                   timestamp: int):
        query = f"""
            SELECT EXISTS(
                SELECT 1
                FROM carmate.{BOOKING_CARPOOLING_TABLE_NAME} rc
                INNER JOIN carmate.{CARPOOLING_TABLE_NAME} c 
                    ON rc.carpooling_id = c.id
                WHERE rc.user_id = %s 
                    AND rc.canceled = 'f'
                    AND c.is_canceled = 'f'
                    AND c.departure_date_time = to_timestamp(%s)
            )
        """

        has_reserved_carpooling: bool = False
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user_id, timestamp))
                except Exception as e:
                    raise InternalServer(str(e))
                has_reserved_carpooling = curs.fetchone()[0]

        return has_reserved_carpooling

    def get_passengers_from_carpooling(self,
                                       carpooling_id: int) -> List[PassengerProfileTable]:
        query = f"""
            SELECT p.*
            FROM carmate.{BOOKING_CARPOOLING_TABLE_NAME} bc
            INNER JOIN carmate.{PASSENGER_PROFILE_TABLE_NAME} p
                ON bc.user_id=p.user_id
            WHERE bc.carpooling_id=%s
        """

        passengers: List[tuple]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (carpooling_id,))
                except Exception as e:
                    raise InternalServer(str(e))
                passengers = curs.fetchall()
        return [PassengerProfileTable(*passenger) for passenger in passengers]

    def get_booked_carpoolings(self,
                               user_id: int) -> List[ReserveCarpoolingTable]:
        query = f"""
            SELECT *
            FROM carmate.{BOOKING_CARPOOLING_TABLE_NAME}
            WHERE user_id=%s
        """

        booking_carpoolings: List[tuple]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user_id,))
                except Exception as e:
                    raise InternalServer(str(e))
                booking_carpoolings = curs.fetchall()
        return [ReserveCarpoolingTable(*booking_carpooling) for booking_carpooling in booking_carpoolings]
