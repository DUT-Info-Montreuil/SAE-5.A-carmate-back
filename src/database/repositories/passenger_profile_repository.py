from abc import ABC
from typing import Tuple

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from database import establishing_connection
from database.exceptions import InternalServer, NotFound, UniqueViolation
from database.repositories import UserRepository
from database.schemas import PassengerProfileTable, UserTable


class PassengerProfileRepositoryInterface(ABC):
    def insert(self,
               user: UserTable) -> PassengerProfileTable: ...

    def get_passenger_by_user_id(self,
                                 user_id: int) -> Tuple[PassengerProfileTable,
                                                        bytes | None]: ...

    def get_passenger(self,
                      passenger_id: int) -> Tuple[PassengerProfileTable,
                                                  bytes | None]: ...


class PassengerProfileRepository(PassengerProfileRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "passengers_profile"

    def insert(self,
               user: UserTable) -> PassengerProfileTable:
        query = f"""
            INSERT INTO carmate.{self.POSTGRES_TABLE_NAME}(user_id)
            VALUES (%s)
            RETURNING id, "description", created_at, user_id
        """

        passenger_profile: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user.id,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                passenger_profile = curs.fetchone()
        return PassengerProfileTable(*passenger_profile)

    def get_passenger(self,
                      passenger_id: int) -> Tuple[PassengerProfileTable,
                                                  bytes | None]:
        query = f"""
            SELECT pp.*, u.profile_picture
            FROM carmate.{self.POSTGRES_TABLE_NAME} pp
            INNER JOIN carmate.{UserRepository.POSTGRES_TABLE_NAME} u
                ON pp.user_id=u.id
            WHERE pp.id=%s
        """

        passenger_data: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (passenger_id,))
                except ProgrammingError:
                    raise NotFound("passenger not found")
                except Exception as e:
                    raise InternalServer(str(e))
                passenger_data = curs.fetchone()

        if passenger_data is None:
            raise NotFound("passenger not found")
        return PassengerProfileTable(*passenger_data[:-1]), passenger_data[-1]

    def get_passenger_by_user_id(self,
                                 user_id: int) -> Tuple[PassengerProfileTable,
                                                        bytes | None]:
        query = f"""
            SELECT pp.*, u.profile_picture
            FROM carmate.{self.POSTGRES_TABLE_NAME} pp
            INNER JOIN carmate.{UserRepository.POSTGRES_TABLE_NAME} u
                ON pp.user_id=u.id
            WHERE pp.user_id=%s
        """

        passenger_data: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user_id,))
                except ProgrammingError:
                    raise NotFound("passenger not found")
                except Exception as e:
                    raise InternalServer(str(e))
                passenger_data = curs.fetchone()

        if passenger_data is None:
            raise NotFound("passenger not found")
        return PassengerProfileTable(*passenger_data[:-1]), passenger_data[-1]
