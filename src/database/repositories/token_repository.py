from abc import ABC
from datetime import datetime

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from api import hash
from database import establishing_connection
from database.exceptions import *
from database.repositories import UserRepository, DriverProfileRepository
from database.schemas import UserTable, TokenTable, DriverProfileTable


class TokenRepositoryInterface(ABC):
    @staticmethod
    def insert(token: str, expiration: datetime, user: UserTable) -> TokenTable: ...
    
    @staticmethod
    def get_expiration(token_hashed: bytes) -> datetime: ...

    @staticmethod
    def get_user(token: bytes) -> UserTable: ...
    
    @staticmethod
    def get_driver_profile(token: bytes) -> DriverProfileTable: ...


class TokenRepository(TokenRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "token"

    @staticmethod
    def insert(token: str, expiration: datetime, user: UserTable) -> TokenTable:
        query = f"""INSERT INTO carmate.{TokenRepository.POSTGRES_TABLE_NAME}
                    VALUES (%s, %s, %s)"""

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (hash(token), expiration, user.id,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
        return TokenTable(token, expiration, user.id)
    
    @staticmethod
    def get_expiration(token_hashed: bytes) -> datetime:
        query = f"""SELECT expire_at 
                    FROM carmate.{TokenRepository.POSTGRES_TABLE_NAME}
                    WHERE token=%s
                    LIMIT 1"""

        expire_at: datetime
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (token_hashed,))
                    expire_at = curs.fetchone()[0]
                except TypeError:
                    raise NotFound("token not found")
                except ProgrammingError:
                    raise NotFound("token not found")
                except IndexError:
                    raise NotFound("token not found")
                except Exception as e:
                    raise InternalServer(str(e))
        return expire_at

    @staticmethod
    def get_user(token: bytes) -> UserTable:
        query = f"""SELECT usr.id, usr.first_name, usr.last_name, usr.email_address, NULL, usr.account_status, usr.created_at, usr.profile_picture
                    FROM carmate."{UserRepository.POSTGRES_TABLE_NAME}" usr
                    INNER JOIN carmate.{TokenRepository.POSTGRES_TABLE_NAME} tkn 
                      ON usr.id = tkn.user_id 
                    WHERE tkn.token=%s"""

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (token,))
                    user = curs.fetchone()
                except ProgrammingError:
                    raise NotFound("token not found")
                except IndexError:
                    raise NotFound("token not found")
                except Exception as e:
                    raise InternalServer(str(e))
        if not user:
            raise NotFound("token not found")
        return UserTable.to_self(user)

    @staticmethod
    def get_driver_profile(token: bytes) -> DriverProfileTable:
        query = f"""SELECT driver.*
                    FROM carmate.{TokenRepository.POSTGRES_TABLE_NAME} as tkn
                    INNER JOIN carmate.{UserRepository.POSTGRES_TABLE_NAME} as usr ON tkn.user_id = usr.id
                    Inner JOIN carmate.{DriverProfileRepository.POSTGRES_TABLE_NAME} as driver ON usr.id = driver.user_id
                    WHERE tkn.token=%s"""

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (token,))
                except ProgrammingError:
                    raise NotFound("driver not found")
                except IndexError:
                    raise NotFound("driver not found")
                except Exception as e:
                    raise InternalServer(str(e))
                driver_profile = curs.fetchone()

        return DriverProfileTable.to_self(driver_profile)

