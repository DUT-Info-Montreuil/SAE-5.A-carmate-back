from datetime import datetime
from typing import List

from psycopg2 import errorcodes

from database import DRIVER_SCHEDULED_CARPOOLING_TABLE_NAME, establishing_connection, InternalServer
from database.interfaces import ScheduledCarpoolingRepositoryInterface
from database.schemas import Weekday, DriverScheduledCarpoolingTable
from psycopg2.errors import lookup, UniqueViolation


class ScheduledCarpoolingRepository(ScheduledCarpoolingRepositoryInterface):

    def insert(self,
               label: str,
               starting_point: List[float],
               destination: List[float],
               start_date: datetime.date,
               end_date: datetime.date,
               start_hour: datetime.time,
               days: List[Weekday],
               max_passengers: int,
               driver_id: int) -> int:
        query = f"""
                INSERT INTO carmate.{DRIVER_SCHEDULED_CARPOOLING_TABLE_NAME} (label, starting_point, destination, start_hour, start_date, end_date, days, max_passengers, driver_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s::weekday[],%s , %s)
                RETURNING id
        """

        propose_id: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (label,
                                         starting_point,
                                         destination,
                                         start_hour,
                                         start_date,
                                         end_date,
                                         [day.name for day in days],
                                         max_passengers,
                                         driver_id))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                propose_id = curs.fetchone()
        if propose_id is None:
            raise InternalServer("Something went wrong")
        return propose_id[0]

    def has_same_time_scheduled_carpooling(self,
                                           start_date: datetime.date,
                                           end_date: datetime.date,
                                           days: List[Weekday],
                                           start_hour: datetime.time,
                                           driver_id: int) -> bool:
        query = f"""
                SELECT EXISTS(
                    SELECT 1
                    FROM carmate.{DRIVER_SCHEDULED_CARPOOLING_TABLE_NAME} AS sc
                    WHERE %s <= sc.end_date 
                        AND sc.start_date <= %s
                        AND sc.days && %s::weekday[] 
                        AND sc.start_hour = %s
                        AND sc.driver_id = %s
                )
        """
        has_same_time: bool = False
        with establishing_connection() as conn:
            with conn.cursor() as curs:

                try:
                    curs.execute(query, (start_date,
                                         end_date,
                                         [day.name for day in days],
                                         start_hour,
                                         driver_id))
                except Exception as e:
                    raise InternalServer(str(e))
                has_same_time = curs.fetchone()[0]

        return has_same_time

    def get_passengers_for_schedule_carpooling(self, schedule_carpooling_id: int) -> List[tuple[int, datetime]]:
        query = """
                WITH ScheduledCarpooling AS (SELECT unnest(sc.days)::weekday AS reserved_day,
                                                    sc.start_date            as start_date_sc,
                                                    sc.end_date              as end_date_sc,
                                                    sc.starting_point,
                                                    sc.destination,
                                                    sc.start_hour,
                                                    sc.max_passengers
                                             FROM carmate.scheduled_carpooling sc
                                             WHERE sc.id = %s),
                     PotentialPassengers as (SELECT psc.passenger_id,
                                                    psc.start_date as start_date_psc,
                                                    psc.end_date   as end_date_psc,
                                                    psc.start_hour,
                                                    sc.start_date_sc,
                                                    sc.end_date_sc,
                                                    sc.reserved_day,
                                                    sc.max_passengers
                                             FROM carmate.propose_scheduled_carpooling psc
                                                      JOIN ScheduledCarpooling sc
                                                           ON
                                                               (psc.start_date, psc.end_date) OVERLAPS
                                                               (sc.start_date_sc, sc.end_date_sc)
                                                                   AND sc.reserved_day = ANY (psc.days)
                                                                   AND psc.start_hour = sc.start_hour
                                                                   AND psc.starting_point = sc.starting_point
                                                                   AND psc.destination = sc.destination),
                     PotentialPassengersWithDates as (SELECT pp.passenger_id,
                                                             pp.reserved_date,
                                                             pp.max_passengers
                                                      FROM (SELECT *,
                                                                   generate_series(
                                                                           GREATEST(start_date_sc, start_date_psc),
                                                                           LEAST(end_date_sc, end_date_psc),
                                                                           '1 day'::interval
                                                                   ) + start_hour AS reserved_date
                                                            FROM PotentialPassengers) pp
                                                      WHERE EXTRACT(DOW FROM pp.reserved_date) = pp.reserved_day::integer),
                     FilteredPotentialPassengersWithDates as (SELECT pp.*,
                                                                     prof.user_id,
                                                                     ROW_NUMBER()
                                                                     OVER (PARTITION BY pp.reserved_date ORDER BY pp.passenger_id) AS row_num
                                                              FROM PotentialPassengersWithDates pp
                                                                       INNER JOIN carmate.passengers_profile prof
                                                                                  ON prof.id = pp.passenger_id
                                                              WHERE NOT EXISTS (SELECT 1
                                                                                FROM carmate.reserve_carpooling rc
                                                                                         INNER JOIN carmate.carpooling c ON rc.carpooling_id = c.id
                                                                                WHERE rc.canceled = false
                                                                                  AND c.is_canceled = false
                                                                                  AND c.departure_date_time = pp.reserved_date
                                                                                  AND rc.user_id = prof.user_id))
                SELECT user_id, reserved_date
                FROM FilteredPotentialPassengersWithDates
                WHERE row_num <= max_passengers
        """
        reservations_to_do: List[tuple[int, datetime.date]]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (schedule_carpooling_id,))
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    reservations_to_do = curs.fetchall()

        return reservations_to_do

    def get_scheduled_carpooling(self, scheduled_carpooling_id: int) -> DriverScheduledCarpoolingTable:
        query = f"""
            SELECT *
            FROM carmate.{DRIVER_SCHEDULED_CARPOOLING_TABLE_NAME} 
            WHERE id = %s
        """
        scheduled_carpooling: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (scheduled_carpooling_id,))
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    reservations_to_do = curs.fetchone()

        return DriverScheduledCarpoolingTable(*reservations_to_do)

    def has_scheduled_with_date_and_day(self,
                                        driver_id: int,
                                        date: datetime.date,
                                        day: Weekday) -> bool:

        query = f"""
            SELECT EXISTS (
                SELECT 1
                FROM carmate.{DRIVER_SCHEDULED_CARPOOLING_TABLE_NAME} sc
                WHERE sc.driver_id = %s
                    AND %s BETWEEN sc.start_date AND sc.end_date
                    AND %s::weekday = ANY(sc.days)
            )
        """
        has_conflict: bool
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (driver_id, date, day.name))
                except Exception as e:
                    raise InternalServer(str(e))
                has_conflict = curs.fetchone()[0]
        return has_conflict
    
    def get_scheduled_carpooling_created_by(self,
                                            driver_id: int) -> List[DriverScheduledCarpoolingTable]:
        query = f"""
            SELECT *
            FROM carmate.{DRIVER_SCHEDULED_CARPOOLING_TABLE_NAME}
            WHERE driver_id=%s
        """

        scheduled_carpoolings: List[tuple]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (driver_id,))
                except Exception as e:
                    raise InternalServer(str(e))
                scheduled_carpoolings = curs.fetchall()
        return [DriverScheduledCarpoolingTable(*scheduled_carpooling) for scheduled_carpooling in scheduled_carpoolings]

