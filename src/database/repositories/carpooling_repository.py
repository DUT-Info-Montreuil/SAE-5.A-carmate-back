from abc import ABC
from datetime import datetime
from typing import List, Tuple

from psycopg2 import ProgrammingError

from api.worker.carpooling.models import CarpoolingForRecap
from database import establishing_connection
from database.exceptions import InternalServer, NotFound
from database.repositories.reserve_carpooling_repository import ReserveCarpoolingRepository


class CarpoolingRepositoryInterface(ABC):
    def get_carpoolings_route(self,
                              start_lat: float,
                              start_lon: float,
                              end_lat: float,
                              end_lon: float,
                              departure_date_time: int,
                              page: int = 1,
                              per_page: int = 10) -> Tuple[int, List[CarpoolingForRecap]] | Tuple[int, List]: ...


class CarpoolingRepository(CarpoolingRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "carpooling"
    RADIUS: float = .07

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
        query = f"""SELECT c.id, c.starting_point, c.destination, c.max_passengers, c.price, c.departure_date_time, c.driver_id
                    FROM carmate.{self.POSTGRES_TABLE_NAME} as c 
                    LEFT JOIN carmate.{ReserveCarpoolingRepository.POSTGRES_TABLE_NAME} as r on (c.id = r.carpooling_id)
                    GROUP BY c.id
                    HAVING ABS(starting_point[1] - %s) < {self.RADIUS} 
                        AND ABS(starting_point[2] - %s) < {self.RADIUS} 
                        AND ABS(destination[1] - %s) < {self.RADIUS}
                        AND ABS(destination[2] - %s) < {self.RADIUS}
                        AND departure_date_time >= to_timestamp(%s)
                    ORDER BY c.id
                    LIMIT {per_page} OFFSET {(page - 1) * per_page}"""

        nb_carpoolings_route: int = 0
        carpoolings_data: List[tuple]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query_nb_carpoolings_route, (start_lat, start_lon, end_lat, end_lon, departure_date_time,))
                except ProgrammingError:
                    return nb_carpoolings_route, []
                except Exception as e:
                    raise InternalServer(str(e))
                
                try:
                    nb_carpoolings_route = curs.fetchone()[0]
                except IndexError:
                    pass

                try:
                    curs.execute(query, (start_lat, start_lon, end_lat, end_lon, departure_date_time,))
                except ProgrammingError:
                    return nb_carpoolings_route, []
                except Exception as e:
                    raise InternalServer(str(e))
                carpoolings_data = curs.fetchall()

        return (nb_carpoolings_route,
                [CarpoolingForRecap.to_self(carpooling) for carpooling in carpoolings_data])
