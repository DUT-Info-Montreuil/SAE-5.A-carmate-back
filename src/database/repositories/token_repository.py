from abc import ABC
from datetime import datetime
from typing import Any

from psycopg2 import errorcodes
from psycopg2.errors import lookup

from api import log, hash
from database import establishing_connection
from database.exceptions import *
from database.schemas import UserTable, TokenTable


class TokenRepositoryInterface(ABC):
    @staticmethod
    def insert(token: str, expiration: datetime, user: UserTable) -> TokenTable: ...


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
            log(e)
            raise InternalServer()
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (hash(token), expiration, user.id,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    log(e)
                    raise UniqueViolation()
                except Exception as e:
                    log(e)
                    raise InternalServer()
            conn.close()
        return TokenTable(token, expiration, user.id)
