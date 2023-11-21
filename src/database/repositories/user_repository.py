from abc import ABC
from typing import Any

from psycopg2 import errorcodes
from psycopg2.errors import lookup

from api import log, hash
from api.worker.auth.models import CredentialDTO
from database import establishing_connection
from database.exceptions import *
from database.schemas import UserTable


class UserRepositoryInterface(ABC):
    @staticmethod
    def insert(credential: CredentialDTO) -> UserTable: ...

    @staticmethod
    def get_user_by_email(email: str) -> UserTable: ...


class UserRepository(UserRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "user"

    @staticmethod
    def insert(credential: CredentialDTO) -> UserTable:
        first_name, last_name, email_address, password = credential.to_json().values()
        query: str = f"""INSERT INTO carmate.{UserRepository.POSTGRES_TABLE_NAME} 
                         VALUES (DEFAULT, %s, %s, %s, %s, DEFAULT) 
                         RETURNING id, first_name, last_name, email_address, password, profile_picture"""

        user: tuple
        try:
            conn = establishing_connection()
        except InternalServer as e:
            log(e)
            raise InternalServer(e)
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (first_name, last_name,
                                         email_address, hash(password),))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    log(e)
                    # Impossible to raise but it is what it is
                    raise UniqueViolation(e)
                except Exception as e:
                    log(e)
                    raise InternalServer(e)
                else:
                    user = curs.fetchone()
            conn.commit()
            conn.close()
        return UserTable.to_self(user)

    @staticmethod
    def get_user_by_email(email: str) -> UserTable:
        query = f"SELECT * FROM carmate.{UserRepository.POSTGRES_TABLE_NAME} WHERE email_address = %s"

        conn: Any
        try:
            conn = establishing_connection()
        except InternalServer as e:
            log(e)
            raise InternalServer()
        except Exception as e:
            log(e)
            raise InternalServer()
        else:
          user_data: tuple
          with conn.cursor() as curs:
              curs.execute(query, (email,))
              user_data = curs.fetchone()

          conn.close()
          if not user_data:
              raise NotFound()
          return UserTable.to_self(user_data)
