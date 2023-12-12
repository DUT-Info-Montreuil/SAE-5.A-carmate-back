from abc import ABC
from typing import List, Tuple

from psycopg2 import ProgrammingError

from database import establishing_connection
from database.exceptions import InternalServer, NotFound
from database.schemas import CarpoolingTable


class CarpoolingRepositoryInterface(ABC):
    def get_carpoolings_route(self,
                              start_lat: float,
                              start_lon: float,
                              end_lat: float,
                              end_lon: float,
                              departure_date_time: int,
                              page: int = 1,
                              per_page: int = 10) -> Tuple[int, List[CarpoolingTable]]: ...


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
                              per_page: int = 10) -> Tuple[int, List[CarpoolingTable]]:
        query_nb_carpoolings_route = f"""
                    SELECT count(id) as nb_carpoolings_route
                    FROM carmate.{self.POSTGRES_TABLE_NAME}
                    WHERE ABS(starting_point[1] - %s) < {self.RADIUS} 
                        AND ABS(starting_point[2] - %s) < {self.RADIUS} 
                        AND ABS(destination[1] - %s) < {self.RADIUS}
                        AND ABS(destination[2] - %s) < {self.RADIUS}
                        AND departure_date_time >= to_timestamp(%s)
        """ 
        query = f"""SELECT *
                    FROM carmate.{self.POSTGRES_TABLE_NAME}
                    WHERE ABS(starting_point[1] - %s) < {self.RADIUS} 
                        AND ABS(starting_point[2] - %s) < {self.RADIUS} 
                        AND ABS(destination[1] - %s) < {self.RADIUS}
                        AND ABS(destination[2] - %s) < {self.RADIUS}
                        AND departure_date_time >= to_timestamp(%s)
                    ORDER BY id
                    LIMIT {per_page} OFFSET {(page - 1) * per_page}"""

        nb_carpoolings_route: int = 0
        carpoolings_data: List[tuple]
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query_nb_carpoolings_route, (start_lat, start_lon, end_lat, end_lon, departure_date_time,))
                except ProgrammingError:
                    raise NotFound("driver not found")
                except Exception as e:
                    raise InternalServer(str(e))
                
                try:
                    nb_carpoolings_route = curs.fetchone()[0]
                except IndexError:
                    pass

                try:
                    curs.execute(query, (start_lat, start_lon, end_lat, end_lon, departure_date_time,))
                except ProgrammingError:
                    raise NotFound("driver not found")
                except Exception as e:
                    raise InternalServer(str(e))
                carpoolings_data = curs.fetchall()

        return (nb_carpoolings_route, 
                [CarpoolingTable.to_self(carpooling) for carpooling in carpoolings_data])
