from abc import ABC
from typing import List, Tuple

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from api.worker.carpooling.models import CarpoolingForRecap
from database import establishing_connection
from database.schemas import CarpoolingTable
from database.repositories.booking_carpooling_repository import BookingCarpoolingRepository
from database.exceptions import (
    InternalServer,
    CheckViolation,
    NotFound
)


class CarpoolingRepositoryInterface(ABC):
    def insert(self,
               driver_id: int,
               starting_point: List[float],
               destination: List[float],
               max_passengers: int,
               price: float,
               departure_date_time: int) -> int: ...

    def get_carpoolings_route(self,
                              start_lat: float,
                              start_lon: float,
                              end_lat: float,
                              end_lon: float,
                              departure_date_time: int,
                              page: int = 1,
                              per_page: int = 10) -> Tuple[int, List[CarpoolingForRecap]] | Tuple[int, List]: ...
    
    def get_from_id(self,
                    carpooling_id: int) -> CarpoolingTable: ...


class CarpoolingRepository(CarpoolingRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "carpooling"
    RADIUS: float = .07

    def insert(self,
               driver_id: int,
               starting_point: List[float],
               destination: List[float],
               max_passengers: int,
               price: float,
               departure_date_time: int) -> int:
        query = f"""
            INSERT INTO carmate.{self.POSTGRES_TABLE_NAME}
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
        query_nb_carpoolings_route = f"""
            SELECT count(id) as nb_carpoolings_route
            FROM carmate.{self.POSTGRES_TABLE_NAME}
            WHERE ABS(starting_point[1] - %s) < {self.RADIUS} 
                AND ABS(starting_point[2] - %s) < {self.RADIUS} 
                AND ABS(destination[1] - %s) < {self.RADIUS}
                AND ABS(destination[2] - %s) < {self.RADIUS}
                AND departure_date_time >= to_timestamp(%s)
        """
        query = f"""
            SELECT c.id, c.starting_point, c.destination, c.max_passengers, c.price, c.departure_date_time, c.driver_id
            FROM carmate.{self.POSTGRES_TABLE_NAME} c 
            LEFT JOIN carmate.{BookingCarpoolingRepository.POSTGRES_TABLE_NAME} r 
                ON c.id=r.carpooling_id
            GROUP BY c.id
            HAVING ABS(starting_point[1] - %s) < {self.RADIUS} 
                AND ABS(starting_point[2] - %s) < {self.RADIUS} 
                AND ABS(destination[1] - %s) < {self.RADIUS}
                AND ABS(destination[2] - %s) < {self.RADIUS}
                AND departure_date_time >= to_timestamp(%s)
            ORDER BY c.id
            LIMIT {per_page} 
            OFFSET {(page - 1) * per_page}
        """

        nb_carpoolings_route: int = 0
        carpoolings_data: List[tuple] = []
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query_nb_carpoolings_route,
                                 (start_lat, start_lon, end_lat, end_lon, departure_date_time,))
                except ProgrammingError:
                    return nb_carpoolings_route, carpoolings_data
                except Exception as e:
                    raise InternalServer(str(e))

                try:
                    nb_carpoolings_route = curs.fetchone()[0]
                except IndexError:
                    pass

                try:
                    curs.execute(query, (start_lat, start_lon, end_lat, end_lon, departure_date_time,))
                except ProgrammingError:
                    return nb_carpoolings_route, carpoolings_data
                except Exception as e:
                    raise InternalServer(str(e))
                carpoolings_data = curs.fetchall()
        return (nb_carpoolings_route,
                [CarpoolingForRecap.to_self(carpooling) for carpooling in carpoolings_data])

    def get_from_id(self,
                    carpooling_id: int) -> CarpoolingTable:
        query = f"""
            SELECT *
            FROM carmate.{self.POSTGRES_TABLE_NAME}
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
        return CarpoolingTable.to_self(carpooling)
