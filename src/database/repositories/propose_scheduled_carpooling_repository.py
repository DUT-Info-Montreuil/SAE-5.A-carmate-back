from datetime import datetime
from typing import List, Tuple

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from database import (
    PASSENGER_SCHEDULED_CARPOOLING_TABLE_NAME,
    PASSENGER_PROFILE_TABLE_NAME,
    BOOKING_CARPOOLING_TABLE_NAME,
    CARPOOLING_TABLE_NAME,
    USER_TABLE_NAME,
    establishing_connection
)
from database.exceptions import UniqueViolation, InternalServer, NotFound
from database.interfaces import ProposeScheduledCarpoolingRepositoryInterface
from database.repositories import PassengerProfileRepository, CarpoolingRepository, BookingCarpoolingRepository
from database.schemas import (
    PassengerScheduledCarpoolingTable,
    CarpoolingTable,
    Weekday
)


class ProposeScheduledCarpoolingRepository(ProposeScheduledCarpoolingRepositoryInterface):
    def insert(self,
               label: str,
               starting_point: List[float],
               destination: List[float],
               start_date: datetime.date,
               end_date: datetime.date,
               start_hour: datetime.time,
               days: List[Weekday],
               passenger_id: int) -> int:
        query = f"""
                INSERT INTO carmate.{PASSENGER_SCHEDULED_CARPOOLING_TABLE_NAME} (label, starting_point, destination, start_hour, start_date, end_date, days, passenger_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s::weekday[], %s)
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
                                         passenger_id))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                propose_id = curs.fetchone()
        if propose_id is None:
            raise InternalServer("Something went wrong")
        return propose_id[0]

    def has_same_time_proposed_scheduled_carpooling(self,
                                                    start_date: datetime.date,
                                                    end_date: datetime.date,
                                                    days: List[Weekday],
                                                    start_hour: datetime.time,
                                                    passenger_id: int) -> bool:
        query = f"""
                SELECT EXISTS(
                    SELECT 1
                    FROM carmate.{PASSENGER_SCHEDULED_CARPOOLING_TABLE_NAME} AS sc
                    WHERE %s <= sc.end_date 
                        AND sc.start_date <= %s
                        AND sc.days && %s::weekday[] 
                        AND sc.start_hour = %s
                        AND sc.passenger_id = %s
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
                                         passenger_id))
                except ProgrammingError:
                    return has_same_time
                except Exception as e:
                    raise InternalServer(str(e))
                has_same_time = curs.fetchone()[0]

        return has_same_time

    def get_user_id_from_scheduled_carpooling(self, propose_scheduled_carpooling_id: int) -> int:
        query = f"""
                SELECT pp.id
                FROM carmate.{PASSENGER_SCHEDULED_CARPOOLING_TABLE_NAME} pc
                INNER JOIN carmate.{PASSENGER_PROFILE_TABLE_NAME} pp ON (pc.passenger_id = pp.id)
                WHERE pc.id = %s
        """
        user_id: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (propose_scheduled_carpooling_id,))
                except ProgrammingError:
                    raise NotFound("User not found for scheduled carpooling")
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    user_id = curs.fetchone()
            if not user_id:
                raise NotFound("User not found for scheduled carpooling")

        return user_id[0]


    def get_carpoolings_to_reserve_for(self, propose_scheduled_carpooling_id: int) -> List[CarpoolingTable]:
        query = f"""
                    WITH ProposedSchedule AS (
                        SELECT
                            pc.id AS propose_carpool_id,
                            unnest(pc.days)::weekday AS reserved_day,
                            pc.start_date,
                            pc.end_date,
                            pc.starting_point,
                            pc.destination,
                            pc.start_hour,
                            pp.user_id
                        FROM carmate.{PASSENGER_SCHEDULED_CARPOOLING_TABLE_NAME} pc
                            INNER JOIN carmate.{PASSENGER_PROFILE_TABLE_NAME} pp ON (pc.passenger_id = pp.id)
                        WHERE pc.id = %s
                    ),
                    ReservationDates AS (
                        SELECT
                            propose_carpool_id,
                            starting_point,
                            destination,
                            start_hour,
                            user_id,
                            reserved_date
                        FROM
                            (
                                SELECT *,
                                    generate_series(start_date, end_date, '1 day'::interval)::DATE AS reserved_date
                                FROM ProposedSchedule
                            ) pc
                        WHERE
                            EXTRACT(DOW FROM pc.reserved_date) = pc.reserved_day::integer
                    ),
                    AlreadyReservedDates AS (
                        SELECT c.departure_date_time::date
                        FROM carmate.{BOOKING_CARPOOLING_TABLE_NAME} rc
                            INNER JOIN carmate.{CARPOOLING_TABLE_NAME} c ON (rc.carpooling_id = c.id)
                            INNER JOIN ReservationDates rd 
                                ON (rd.user_id = rc.user_id)
                        WHERE rd.reserved_date = c.departure_date_time::date
                            AND rd.start_hour = c.departure_date_time::time
                    ),
                    ReservationDatesFiltered AS (
                        SELECT *
                        FROM ReservationDates
                        WHERE reserved_date NOT IN (SELECT departure_date_time FROM AlreadyReservedDates)
                    ),
                    NumberOfReservations AS (
                        SELECT rc.carpooling_id, 
                            COUNT(*) AS reserved
                        FROM carmate.reserve_carpooling rc
                        WHERE NOT rc.canceled
                        GROUP BY rc.carpooling_id
                    )
                    SELECT DISTINCT ON (c.departure_date_time) c.*
                    FROM
                        carmate.{CARPOOLING_TABLE_NAME} c
                    INNER JOIN ReservationDatesFiltered rd 
                        ON c.starting_point = rd.starting_point
                        AND c.destination = rd.destination
                        AND c.departure_date_time::date = rd.reserved_date
                        AND c.departure_date_time::time = rd.start_hour
                    LEFT JOIN NumberOfReservations nr 
                        ON c.id = nr.carpooling_id
                    WHERE COALESCE(nr.reserved, 0) < c.max_passengers;
        """
        carpoolings_to_reserve: List[tuple] = []
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (propose_scheduled_carpooling_id,))
                except ProgrammingError:
                    pass
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    carpoolings_to_reserve = curs.fetchall()

        return [CarpoolingTable(*tpl) for tpl in carpoolings_to_reserve]

    def get_matching_proposed_scheduled_carpooling(self,
                                                   starting_point: List[float],
                                                   destination: List[float],
                                                   date: datetime.date,
                                                   time: datetime.time,
                                                   limit: int) -> List[int]:
        query = f"""
                    WITH ProposedSchedule AS (
                        SELECT
                            pc.id AS propose_carpool_id,
                            unnest(pc.days)::weekday AS reserved_day,
                            pc.start_date,
                            pc.end_date,
                            pc.starting_point,
                            pc.destination,
                            pc.start_hour,
                            pp.user_id
                        FROM carmate.{PASSENGER_SCHEDULED_CARPOOLING_TABLE_NAME} pc
                        INNER JOIN carmate.{PASSENGER_PROFILE_TABLE_NAME} pp ON (pc.passenger_id = pp.id)
                        WHERE pc.starting_point = %s::double precision[] 
                            AND pc.destination = %s::double precision[]
                            AND %s BETWEEN pc.start_date AND pc.end_date
                            AND pc.start_hour = %s
                    ),
                    ReservationDates AS (
                        SELECT
                            propose_carpool_id,
                            starting_point,
                            destination,
                            start_hour,
                            user_id,
                            reserved_date
                        FROM
                            (
                                SELECT *,
                                    generate_series(start_date, end_date, '1 day'::interval)::DATE AS reserved_date
                                FROM ProposedSchedule
                            ) pc
                        WHERE EXTRACT(DOW FROM pc.reserved_date) = pc.reserved_day::integer
                    ),
                    AlreadyReservedDates AS (
                        SELECT c.departure_date_time::date
                        FROM carmate.{BOOKING_CARPOOLING_TABLE_NAME} rc
                            INNER JOIN carmate.{CARPOOLING_TABLE_NAME} c ON (rc.carpooling_id = c.id)
                            INNER JOIN ReservationDates rd ON (rd.user_id = rc.user_id)
                        WHERE rd.reserved_date = c.departure_date_time::date
                            AND rd.start_hour = c.departure_date_time::time
                    ),
                    ReservationDatesFiltered AS (
                        SELECT *
                        FROM ReservationDates
                        WHERE reserved_date NOT IN (SELECT departure_date_time FROM AlreadyReservedDates)
                    )
                    SELECT propose_carpool_id
                    FROM ReservationDatesFiltered
                    WHERE reserved_date = %s
                    LIMIT %s
        """
        carpoolings_ids: List[tuple] = []
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (starting_point,
                                         destination,
                                         date,
                                         time,
                                         date,
                                         limit))
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    carpoolings_ids = curs.fetchall()

        return [carpoolings_id[0] for carpoolings_id in carpoolings_ids]

    def has_scheduled_with_date_and_day(self,
                                        passenger_id: int,
                                        date: datetime.date,
                                        day: Weekday) -> bool:
        query = f"""
            SELECT EXISTS (
                SELECT 1
                FROM carmate.{PASSENGER_SCHEDULED_CARPOOLING_TABLE_NAME} pc
                WHERE pc.passenger_id = %s
                    AND %s BETWEEN pc.start_date AND pc.end_date
                    AND %s::weekday = ANY(pc.days)
                LIMIT 1
            )
        """
        has_conflict: bool
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (passenger_id, date, day.name))
                except Exception as e:
                    raise InternalServer(str(e))
                has_conflict = curs.fetchone()[0]
        return has_conflict

    def get_carpoolings_to_create_and_reserve_for(self, propose_scheduled_carpooling_id: int) -> List[tuple[int, datetime, int, List[float], List[float]]]:
        query = f"""
                WITH ProposedScheduled AS (SELECT psc.starting_point,
                                                  psc.destination,
                                                  psc.start_date            as start_date_psc,
                                                  psc.end_date              as end_date_psc,
                                                  psc.start_hour,
                                                  unnest(psc.days)::weekday as reserved_day,
                                                  pp.user_id
                                           FROM carmate.propose_scheduled_carpooling psc
                                                    INNER JOIN carmate.passengers_profile pp on psc.passenger_id = pp.id
                                           WHERE psc.id = %s
                ),
                     PotentialScheduledCarpooling AS (SELECT sc.driver_id,
                                                             sc.start_date as start_date_sc,
                                                             sc.end_date   as end_date_sc,
                                                             sc.max_passengers,
                                                             sc.starting_point,
                                                             sc.destination,
                                                             psc.start_hour,
                                                             psc.start_date_psc,
                                                             psc.reserved_day,
                                                             psc.end_date_psc
                                                      FROM carmate.scheduled_carpooling sc
                                                               JOIN ProposedScheduled psc
                                                                    ON (psc.start_date_psc, psc.end_date_psc) OVERLAPS
                                                                       (sc.start_date, sc.end_date)
                                                                        AND psc.reserved_day = ANY (sc.days)
                                                                        AND psc.start_hour = sc.start_hour
                                                                        AND psc.starting_point = sc.starting_point
                                                                        AND psc.destination = sc.destination),
                     PotentialScheduledCarpoolingsWithDates as (SELECT potsc.driver_id,
                                                                       potsc.reserved_date,
                                                                       potsc.max_passengers,
                                                                       potsc.starting_point,
                                                                       potsc.destination
                                                                FROM (SELECT *,
                                                                             generate_series(
                                                                                     GREATEST(start_date_sc, start_date_psc),
                                                                                     LEAST(end_date_sc, end_date_psc),
                                                                                     '1 day'::interval
                                                                             ) + start_hour AS reserved_date
                                                                      FROM PotentialScheduledCarpooling) potsc
                                                                WHERE EXTRACT(DOW FROM potsc.reserved_date) = potsc.reserved_day::integer),
                     FilteredPotentialScheduledCarpoolingsWithDates as (SELECT *,
                                                                               ROW_NUMBER() OVER (PARTITION BY potsc.reserved_date) AS row_num
                                                                        FROM PotentialScheduledCarpoolingsWithDates potsc
                                                                        WHERE NOT EXISTS (SELECT 1
                                                                                          FROM carmate.carpooling c
                                                                                          WHERE c.is_canceled = false
                                                                                            AND c.departure_date_time = potsc.reserved_date
                                                                                            AND c.driver_id = potsc.driver_id))
                SELECT driver_id,
                       reserved_date,
                       max_passengers,
                       starting_point,
                       destination
                FROM FilteredPotentialScheduledCarpoolingsWithDates
                WHERE row_num = 1
        """
        carpoolings_to_create_and_reserve: List[tuple[int, datetime, int, List[float], List[float]]]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (propose_scheduled_carpooling_id,))
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    carpoolings_to_create_and_reserve = curs.fetchall()

        return carpoolings_to_create_and_reserve
    
    def get_propose_scheduled_carpoolings_from_user_id(self,
                                                       user_id: int) -> List[Tuple[CarpoolingTable, int, str, str]]:
        query = f"""
            WITH ProposedSchedule AS (
                SELECT pc.id AS propose_carpool_id,
                       unnest(pc.days)::weekday AS reserved_day,
                       pc.start_date,
                       pc.end_date,
                       pc.starting_point,
                       pc.destination,
                       pc.start_hour,
                       pp.user_id
                FROM carmate.{PASSENGER_SCHEDULED_CARPOOLING_TABLE_NAME} pc
                INNER JOIN carmate.{PASSENGER_PROFILE_TABLE_NAME} pp
                    ON pc.passenger_id=pp.id
                WHERE pp.user_id=%s
            ),
            ReservationDates AS (
                SELECT propose_carpool_id,
                       starting_point,
                       destination,
                       start_hour,
                       user_id,
                       reserved_date
                FROM (SELECT *,
                             generate_series(start_date, 
                                             end_date, 
                                             '1 day'::interval)::DATE AS reserved_date
                      FROM ProposedSchedule) pc
                WHERE EXTRACT(DOW FROM pc.reserved_date)=pc.reserved_day::integer
            ),
            AlreadyReservedDates AS (
                SELECT c.*,
                       0 as seats_taken,
                       1 as user_id
                FROM carmate.{BOOKING_CARPOOLING_TABLE_NAME} rc
                INNER JOIN carmate.{CARPOOLING_TABLE_NAME} c 
                    ON rc.carpooling_id=c.id
                INNER JOIN ReservationDates rd 
                    ON rd.user_id=rc.user_id
                WHERE rd.reserved_date=c.departure_date_time::date
                    AND rd.start_hour=c.departure_date_time::time
                GROUP BY c.id
            )
            SELECT ard.id,
                   ard.starting_point,
                   ard.destination,
                   ard.max_passengers,
                   ard.departure_date_time,
                   ard.is_canceled,
                   ard.driver_id,
                   ard.seats_taken,
                   u.first_name,
                   u.last_name
            FROM AlreadyReservedDates ard
            INNER JOIN carmate.{USER_TABLE_NAME} u
                ON ard.user_id=u.id
        """

        propose_scheduled_carpoolings: List[tuple]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user_id,))
                except Exception as e:
                    raise InternalServer(str(e))
                propose_scheduled_carpoolings = curs.fetchall()
        nb_field = len(CarpoolingTable.__dict__.keys())
        return [(CarpoolingTable(*propose_scheduled_carpooling[:nb_field]),
                 propose_scheduled_carpooling[nb_field],
                 propose_scheduled_carpooling[nb_field + 1],
                 propose_scheduled_carpooling[nb_field + 2]) 
                 for propose_scheduled_carpooling in propose_scheduled_carpoolings]
