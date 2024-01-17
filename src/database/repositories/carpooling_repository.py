from datetime import datetime
from typing import List, Tuple

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from api.worker.carpooling.models import CarpoolingForRecap
from api.worker.user.models import PublishedCarpoolingDTO
from database import (
    CARPOOLING_TABLE_NAME,
    BOOKING_CARPOOLING_TABLE_NAME,
    establishing_connection
)
from database.interfaces import CarpoolingRepositoryInterface
from database.exceptions import (
    InternalServer,
    CheckViolation,
    NotFound
)
from database.schemas import CarpoolingTable, Weekday


class CarpoolingRepository(CarpoolingRepositoryInterface):
    RADIUS: float = .07

    def insert(self,
               driver_id: int,
               starting_point: List[float],
               destination: List[float],
               max_passengers: int,
               price: float,
               departure_date_time: int) -> int:
        query = f"""
            INSERT INTO carmate.{CARPOOLING_TABLE_NAME}
            VALUES (DEFAULT, %s, %s, %s, %s, DEFAULT, to_timestamp(%s), %s)
            RETURNING id
        """

        carpooling_id: int
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (
                        starting_point, destination, max_passengers, price,
                        departure_date_time, driver_id))
                except lookup(errorcodes.CHECK_VIOLATION):
                    raise CheckViolation("The starting point or end point is out of France bounds")
                except Exception as e:
                    raise InternalServer(str(e))
                carpooling_id = curs.fetchone()
        return carpooling_id[0]

    def get_carpoolings_route(self,
                              start_lat: float,
                              start_lon: float,
                              end_lat: float,
                              end_lon: float,
                              departure_date_time: int,
                              page: int = 1,
                              per_page: int = 10) -> Tuple[int, List[CarpoolingForRecap]] | Tuple[int, List]:
        query = f"""
                WITH Carpoolings as (SELECT c.id                  as id,
                                            c.starting_point      as starting_point,
                                            c.destination         as destination,
                                            c.max_passengers      as max_passengers,
                                            c.price               as price,
                                            c.departure_date_time as departure_date_time,
                                            c.driver_id           as driver_id,
                                            count(r.user_id)      as seats_taken
                                     FROM carmate.carpooling c
                                              LEFT JOIN carmate.reserve_carpooling r
                                                        ON c.id = r.carpooling_id
                                     GROUP BY c.id
                                     HAVING ABS(starting_point[1] - %s) < {self.RADIUS}
                                        AND ABS(starting_point[2] - %s) < {self.RADIUS}
                                        AND ABS(destination[1] - %s) < {self.RADIUS}
                                        AND ABS(destination[2] - %s) < {self.RADIUS}
                                        AND departure_date_time BETWEEN to_timestamp(%s) - INTERVAL '1 hour' AND to_timestamp(%s) + INTERVAL '1 hour'),
                     PotentialScheduledCarpooling as (SELECT sc.id                    as id,
                                                             sc.starting_point        as starting_point,
                                                             sc.destination           as destination,
                                                             sc.max_passengers        as max_passengers,
                                                             0                        as price,
                                                             (to_timestamp(%s)::date + sc.start_hour)         as departure_date_time, -- yes there is a problem here but amen deadline is coming
                                                             sc.driver_id             as driver_id,
                                                             0                        as seats_taken,
                                                             unnest(sc.days)::weekday as reserved_day,
                                                             sc.start_hour            as start_hour
                                                      FROM carmate.scheduled_carpooling sc
                                                      WHERE ABS(starting_point[1] - %s) < {self.RADIUS}
                                                        AND ABS(starting_point[2] - %s) < {self.RADIUS}
                                                        AND ABS(destination[1] - %s) < {self.RADIUS}
                                                        AND ABS(destination[2] - %s) < {self.RADIUS}
                                                        AND (
                                                          to_timestamp(%s) + INTERVAL '1 hour' BETWEEN sc.start_date AND sc.end_date
                                                              OR
                                                          to_timestamp(%s) - INTERVAL '1 hour' BETWEEN sc.start_date AND sc.end_date
                                                          )),
                     PotentialScheduledCarpoolingWithDate as (SELECT id,
                                                                     starting_point,
                                                                     destination,
                                                                     max_passengers,
                                                                     price,
                                                                     departure_date_time,
                                                                     driver_id,
                                                                     seats_taken
                                                              FROM PotentialScheduledCarpooling
                                                              WHERE reserved_day::integer = EXTRACT(DOW FROM to_timestamp(%s))),
                     FilteredScheduledCarpoolingWithDate as (SELECT psc.*
                                                             FROM PotentialScheduledCarpoolingWithDate psc
                                                             WHERE NOT EXISTS (SELECT 1
                                                                               FROM carmate.carpooling c
                                                                               WHERE c.driver_id = psc.driver_id
                                                                                 AND is_canceled = false
                                                                                 AND c.departure_date_time = psc.departure_date_time)),
                     Results as ((SELECT *, false as is_scheduled
                                  FROM Carpoolings)
                                 UNION
                                 (SELECT *, true as is_scheduled
                                  FROM FilteredScheduledCarpoolingWithDate))
                SELECT *, (SELECT COUNT(*) FROM Results)
                FROM Results
                LIMIT {per_page} 
                OFFSET {(page - 1) * per_page}
        """

        nb_carpoolings_route: int = 0
        carpoolings_data: List[tuple] = []
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query,
                                 (start_lat, start_lon, end_lat, end_lon, departure_date_time, departure_date_time, departure_date_time, start_lat, start_lon, end_lat, end_lon, departure_date_time, departure_date_time, departure_date_time))
                except Exception as e:
                    raise InternalServer(str(e))
                carpoolings_data = curs.fetchall()
                if len(carpoolings_data) == 0:
                    return nb_carpoolings_route, carpoolings_data

        return (carpoolings_data[0][-1],
                [CarpoolingForRecap.to_self(carpooling[0:-1]) for carpooling in carpoolings_data])

    def get_from_id(self,
                    carpooling_id: int) -> CarpoolingTable:
        query = f"""
            SELECT *
            FROM carmate.{CARPOOLING_TABLE_NAME}
            WHERE id=%s
        """

        carpooling: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (carpooling_id,))
                except ProgrammingError:
                    raise NotFound("carpooling not found")
                except Exception as e:
                    raise InternalServer(str(e))
                carpooling = curs.fetchone()
        
        if carpooling is None:
            raise NotFound("carpooling not found")
        return CarpoolingTable(*carpooling)

    def get_last_carpooling_between(self, driver_id: int, user_id: int) -> CarpoolingTable:
        query = f"""
             SELECT c.*
             FROM carmate.{CARPOOLING_TABLE_NAME} c
             LEFT JOIN carmate.{BOOKING_CARPOOLING_TABLE_NAME} r 
                 ON c.id=r.carpooling_id
             WHERE c.driver_id=%s 
                 AND r.user_id=%s
                 AND r.canceled='f'
                 AND r.passenger_code_validated='t' 
                 AND c.is_canceled='f'
             ORDER BY c.departure_date_time DESC
             LIMIT 1
        """

        carpooling: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (driver_id, user_id))
                except ProgrammingError:
                    raise NotFound("There are no carpooling existing between these two users")
                except Exception as e:
                    raise InternalServer(str(e))
                carpooling = curs.fetchone()

        if carpooling is None:
            raise NotFound("There are no carpooling existing between these two users")
        return CarpoolingTable(*carpooling)

    def has_carpooling_between_dates_at_hour(self,
                                             start_date: datetime.date,
                                             end_date: datetime.date,
                                             at_time: datetime.time,
                                             on_days: List[Weekday],
                                             driver_id: int) -> bool:
        query = f"""
            SELECT EXISTS(
                SELECT 1
                FROM carmate.{CARPOOLING_TABLE_NAME}
                WHERE driver_id=%s 
                    AND is_canceled=false
                    AND EXTRACT(ISODOW FROM departure_date_time) IN %s
                    AND departure_date_time BETWEEN to_date(%s) AND to_date(%s)
                    AND departure_date_time::time = %s
                LIMIT 1
            )
        """

        has_carpooling: bool = False
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (driver_id, on_days, start_date, end_date, at_time))
                except ProgrammingError:
                    return has_carpooling
                except Exception as e:
                    raise InternalServer(str(e))
                has_carpooling = curs.fetchone()[0]
        return has_carpooling

    def has_carpooling_at(self,
                          driver_id: int,
                          timestamp: int) -> bool:
        query = f"""
            SELECT EXISTS(
                SELECT 1
                FROM carmate.{CARPOOLING_TABLE_NAME}
                WHERE driver_id=%s 
                    AND is_canceled=false
                    AND departure_date_time = to_timestamp(%s)
            )
        """
        has_carpooling: bool = False
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (driver_id, timestamp))
                except Exception as e:
                    raise InternalServer(str(e))
                has_carpooling = curs.fetchone()[0]
        return has_carpooling

    def get_carpooling_created_by(self,
                                  driver_id: int) -> List[PublishedCarpoolingDTO]:
        query = f"""
            SELECT c.*, count(r.user_id) as seats_taken
            FROM carmate.{CARPOOLING_TABLE_NAME} c
            LEFT JOIN carmate.{BOOKING_CARPOOLING_TABLE_NAME} r
                ON c.id = r.carpooling_id
            GROUP BY c.id
            HAVING driver_id=%s
        """

        carpoolings: List[tuple]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (driver_id,))
                except Exception as e:
                    raise InternalServer(str(e))
                carpoolings = curs.fetchall()
        return [PublishedCarpoolingDTO(*carpooling, []) for carpooling in carpoolings]

    def get_carpooling_by_scheduled_carpooling_and_date(self,
                                                        scheduled_carpooling_id: int,
                                                        date: datetime.date):
        query = f"""
                WITH ScheduledCarpooling AS (SELECT start_date, end_date, start_hour, unnest(days) as reserved_day, driver_id
                                             FROM carmate.scheduled_carpooling
                                             WHERE id = %s),
                     ScheduledCarpoolingWithFilteredDates AS (SELECT *
                                                              FROM (SELECT *,
                                                                           generate_series(start_date, end_date, '1 day'::interval) as days
                                                                    FROM ScheduledCarpooling) sc
                                                              WHERE EXTRACT(DOW FROM sc.days) = sc.reserved_day::integer
                                                                AND sc.days = %s)
                SELECT id
                FROM carmate.carpooling c
                         INNER JOIN ScheduledCarpoolingWithFilteredDates sc
                                    ON (c.driver_id = sc.driver_id)
                                        AND (c.departure_date_time = sc.days + sc.start_hour)
        """
        carpooling_id: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (scheduled_carpooling_id, date))
                except Exception as e:
                    raise InternalServer(str(e))
                carpooling_id = curs.fetchone()

        if not carpooling_id or len(carpooling_id) == 0:
            raise NotFound("Carpooling not found")

        return carpooling_id[0]

