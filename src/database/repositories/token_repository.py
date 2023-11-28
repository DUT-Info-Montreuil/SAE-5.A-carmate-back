from abc import ABC
from datetime import datetime
from typing import Any

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from api import hash
from database import establishing_connection
from database.exceptions import *
from database.repositories import UserRepository
from database.schemas import UserTable, TokenTable


class TokenRepositoryInterface(ABC):
    @staticmethod
    def insert(token: str, expiration: datetime, user: UserTable) -> TokenTable: ...
    @staticmethod
    def get_expiration(token_hashed: bytes) -> datetime: ...

    @staticmethod
    def get_user(token: bytes) -> UserTable: ...


class TokenRepository(TokenRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "token"

    @staticmethod
    def insert(token: str, expiration: datetime, user: UserTable) -> TokenTable:
        query = f"""INSERT INTO carmate.{TokenRepository.POSTGRES_TABLE_NAME}
                    VALUES (%s, %s, %s)"""

        conn: Any
        try:
            conn = establishing_connection()
        except InternalServer as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (hash(token), expiration, user.id,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
            conn.commit()
            conn.close()
        return TokenTable(token, expiration, user.id)
    
    @staticmethod
    def get_expiration(token_hashed: bytes) -> datetime:
        query = f"""SELECT expire_at 
                    FROM carmate.{TokenRepository.POSTGRES_TABLE_NAME}
                    WHERE token=%s
                    LIMIT 1"""

        conn: Any
        expire_at: datetime
        try:
            conn = establishing_connection()
        except InternalServer as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (token_hashed,))
                    expire_at = curs.fetchone()[0]
                except ProgrammingError:
                    raise NotFound("token not found")
                except IndexError:
                    raise NotFound("token not found")
                except Exception as e:
                    raise InternalServer(str(e))
            conn.commit()
            conn.close()

        return expire_at

    @staticmethod
    def get_user(token: bytes) -> UserTable:
        query = f"""SELECT usr.id, usr.first_name, usr.last_name, usr.email_address, NULL, usr.account_status, usr.profile_picture
                    FROM carmate."{UserRepository.POSTGRES_TABLE_NAME}" usr
                    INNER JOIN carmate.{TokenRepository.POSTGRES_TABLE_NAME} tkn 
                      ON usr.id = tkn.user_id 
                    WHERE tkn.token=%s"""

        conn: Any
        try:
            conn = establishing_connection()
        except InternalServer as e:
            raise InternalServer(str(e))
        else:
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
            conn.close()
        return UserTable.to_self(user)
