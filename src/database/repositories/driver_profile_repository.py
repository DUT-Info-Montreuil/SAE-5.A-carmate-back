from abc import ABC

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from database import establishing_connection
from database.exceptions import InternalServer, NotFound, UniqueViolation
from database.schemas import DriverProfileTable, UserTable


class DriverProfileRepositoryInterface(ABC):
    def insert(self,
               user: UserTable) -> DriverProfileTable: ...

    def get_driver_by_user_id(self,
                              user_id: int) -> DriverProfileTable: ...

    def get_driver(self,
                   driver_id: int) -> DriverProfileTable: ...


class DriverProfileRepository(DriverProfileRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "driver_profile"

    def insert(self,
               user: UserTable) -> DriverProfileTable:
        query = f"""
            INSERT INTO carmate.{self.POSTGRES_TABLE_NAME}(user_id)
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
        return DriverProfileTable.to_self(conducteur_profile)

    def get_driver(self,
                   driver_id: int) -> DriverProfileTable:
        query = f"""
            SELECT * 
            FROM carmate.{self.POSTGRES_TABLE_NAME} 
            WHERE id=%s
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
        return DriverProfileTable.to_self(driver_data)

    def get_driver_by_user_id(self,
                              user_id: int) -> DriverProfileTable:
        query = f"""
            SELECT * 
            FROM carmate.{self.POSTGRES_TABLE_NAME} 
            WHERE user_id=%s
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
        return DriverProfileTable.to_self(driver_data)
