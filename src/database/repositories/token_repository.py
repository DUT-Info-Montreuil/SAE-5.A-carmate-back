from abc import ABC
from datetime import datetime

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from api import hash
from database import establishing_connection
from database.exceptions import *
from database.repositories import (
    UserRepository,
    DriverProfileRepository,
    PassengerProfileRepository, token_table_name, user_table_name, driver_profile_table_name,
    passenger_profile_table_name
)
from database.schemas import (
    UserTable,
    TokenTable,
    DriverProfileTable,
    PassengerProfileTable
)


class TokenRepositoryInterface(ABC):
    def insert(self,
            token: str, 
            expiration: datetime, 
            user: UserTable) -> TokenTable: ...

    def get_expiration(self,
                       token_hashed: bytes) -> datetime: ...

    def get_user(self,
                 token: bytes) -> UserTable: ...
    
    def get_driver_profile(self,
                           token: bytes) -> DriverProfileTable: ...
    def get_passenger_profile(self,
                              token: bytes) -> PassengerProfileTable: ...


class TokenRepository(TokenRepositoryInterface):
    def insert(self,
               token: str,
               expiration: datetime,
               user: UserTable) -> TokenTable:
        query = f"""
            INSERT INTO carmate.{token_table_name}
            VALUES (%s, %s, %s)
        """

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (hash(token), expiration, user.id,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
        return TokenTable(token, expiration, user.id)
    
    def get_expiration(self,
                       token_hashed: bytes) -> datetime:
        query = f"""
            SELECT expire_at 
            FROM carmate.{token_table_name}
            WHERE token=%s
            LIMIT 1
        """

        expire_at: datetime
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (token_hashed,))
                except ProgrammingError:
                    raise NotFound("token not found")
                except Exception as e:
                    raise InternalServer(str(e))
                expire_at = curs.fetchone()
        
        if expire_at is None:
            raise NotFound("token not found")
        return expire_at[0]

    def get_user(self,
                 token: bytes) -> UserTable:
        query = f"""
            SELECT usr.id, usr.first_name, usr.last_name, usr.email_address, NULL, usr.account_status, usr.created_at, usr.profile_picture
            FROM carmate."{user_table_name}" usr
            INNER JOIN carmate.{token_table_name} tkn 
                ON usr.id = tkn.user_id 
            WHERE tkn.token=%s
        """

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (token,))
                except ProgrammingError:
                    raise NotFound("token not found")
                except Exception as e:
                    raise InternalServer(str(e))
                user = curs.fetchone()
    
        if user is None:
            raise NotFound("token not found")
        return UserTable(*user)

    def get_driver_profile(self,
                           token: bytes) -> DriverProfileTable:
        query = f"""
            SELECT driver.*
            FROM carmate.{token_table_name} AS tkn
            INNER JOIN carmate.{user_table_name} AS usr 
                ON tkn.user_id = usr.id
            Inner JOIN carmate.{driver_profile_table_name} AS driver 
                ON usr.id = driver.user_id
            WHERE tkn.token=%s
        """

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (token,))
                except ProgrammingError:
                    raise NotFound("driver not found")
                except Exception as e:
                    raise InternalServer(str(e))
                driver_profile = curs.fetchone()
                if driver_profile is None:
                    raise NotFound("driver not found")
        return DriverProfileTable(*driver_profile)

    def get_passenger_profile(self, token: bytes) -> DriverProfileTable:
        query = f"""
            SELECT passenger.*
            FROM carmate.{token_table_name} tkn
            INNER JOIN carmate.{user_table_name} usr 
                ON tkn.user_id=usr.id
            INNER JOIN carmate.{passenger_profile_table_name} passenger 
                ON usr.id=passenger.user_id
            WHERE tkn.token=%s
        """

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (token,))
                except ProgrammingError:
                    raise NotFound("passenger not found")
                except IndexError:
                    raise NotFound("passenger not found")
                except Exception as e:
                    raise InternalServer(str(e))
                passenger_profile = curs.fetchone()

        if passenger_profile is None:
            raise NotFound("passenger not found")
        return PassengerProfileTable(*passenger_profile)
