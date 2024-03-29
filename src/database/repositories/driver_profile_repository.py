from typing import Tuple

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from database import (
    DRIVER_PROFILE_TABLE_NAME,
    USER_TABLE_NAME,
    establishing_connection
)
from database.interfaces import DriverProfileRepositoryInterface
from database.exceptions import (
    InternalServer,
    NotFound,
    UniqueViolation
)
from database.schemas import DriverProfileTable, UserTable


class DriverProfileRepository(DriverProfileRepositoryInterface):
    def insert(self,
               user: UserTable) -> DriverProfileTable:
        query = f"""
            INSERT INTO carmate.{DRIVER_PROFILE_TABLE_NAME}(user_id)
            VALUES (%s)
            RETURNING id, "description", created_at, user_id
        """

        conducteur_profile: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user.id,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                conducteur_profile = curs.fetchone()
        return DriverProfileTable(*conducteur_profile)

    def get_driver(self,
                   driver_id: int) -> Tuple[DriverProfileTable,
                                            bytes | None]:
        query = f"""
            SELECT dp.*, u.profile_picture
            FROM carmate.{DRIVER_PROFILE_TABLE_NAME} dp
            INNER JOIN carmate.{USER_TABLE_NAME} u
                ON dp.user_id=u.id
            WHERE dp.id=%s
        """

        driver_data: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (driver_id,))
                except ProgrammingError:
                    raise NotFound("driver not found")
                except Exception as e:
                    raise InternalServer(str(e))
                driver_data = curs.fetchone()

        if driver_data is None:
            raise NotFound("driver not found")
        return DriverProfileTable(*driver_data[:-1]), driver_data[-1]

    def get_driver_by_user_id(self,
                              user_id: int) -> Tuple[DriverProfileTable, 
                                                     bytes | None]:
        query = f"""
            SELECT dp.*, u.profile_picture
            FROM carmate.{DRIVER_PROFILE_TABLE_NAME} dp
            INNER JOIN carmate.{USER_TABLE_NAME} u
                ON dp.user_id=u.id
            WHERE dp.user_id=%s
        """

        driver_data: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user_id,))
                except ProgrammingError:
                    raise NotFound("driver not found")
                except Exception as e:
                    raise InternalServer(str(e))
                driver_data = curs.fetchone()

        if driver_data is None:
            raise NotFound("driver not found")
        return DriverProfileTable(*driver_data[:-1]), driver_data[-1]
