from datetime import datetime

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from api import hash
from database import (
    TOKEN_TABLE_NAME,
    USER_TABLE_NAME,
    DRIVER_PROFILE_TABLE_NAME,
    PASSENGER_PROFILE_TABLE_NAME,
    establishing_connection
)
from database.interfaces import TokenRepositoryInterface
from database.exceptions import *
from database.schemas import (
    UserTable,
    TokenTable,
    DriverProfileTable,
    PassengerProfileTable
)


class TokenRepository(TokenRepositoryInterface):
    def insert(self,
               token: str,
               expiration: datetime,
               user: UserTable) -> TokenTable:
        query = f"""
            INSERT INTO carmate.{TOKEN_TABLE_NAME}
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
            FROM carmate.{TOKEN_TABLE_NAME}
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
            FROM carmate."{USER_TABLE_NAME}" usr
            INNER JOIN carmate.{TOKEN_TABLE_NAME} tkn 
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
            FROM carmate.{TOKEN_TABLE_NAME} AS tkn
            INNER JOIN carmate.{USER_TABLE_NAME} AS usr 
                ON tkn.user_id = usr.id
            Inner JOIN carmate.{DRIVER_PROFILE_TABLE_NAME} AS driver 
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
        return DriverProfileTable(*driver_profile)

    def get_passenger_profile(self, token: bytes) -> DriverProfileTable:
        query = f"""
            SELECT passenger.*
            FROM carmate.{TOKEN_TABLE_NAME} tkn
            INNER JOIN carmate.{USER_TABLE_NAME} usr 
                ON tkn.user_id=usr.id
            INNER JOIN carmate.{PASSENGER_PROFILE_TABLE_NAME} passenger 
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
