from abc import ABC
from typing import Any

from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from api import hash
from api.worker.auth.models import CredentialDTO
from api.worker.user import AccountStatus
from database import establishing_connection
from database.exceptions import *
from database.schemas import UserTable


class UserRepositoryInterface(ABC):
    @staticmethod
    def insert(credential: CredentialDTO, account_status: AccountStatus) -> UserTable: ...

    @staticmethod
    def get_user_by_email(email: str) -> UserTable: ...

    @staticmethod
    def get_user_by_id(id: int) -> UserTable: ...


class UserRepository(UserRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "user"

    @staticmethod
    def insert(credential: CredentialDTO, account_status: AccountStatus) -> UserTable:
        first_name, last_name, email_address, password = credential.to_json().values()
        query: str = f"""INSERT INTO carmate.{UserRepository.POSTGRES_TABLE_NAME}(first_name, last_name, email_address, password, account_status)
                         VALUES (%s, %s, %s, %s, %s) 
                         RETURNING id, first_name, last_name, email_address, password, account_status, created_at, profile_picture"""

        user: tuple
        try:
            conn = establishing_connection()
        except InternalServer as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (first_name, last_name,
                                         email_address, hash(password), account_status.name,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    user = curs.fetchone()
            conn.commit()
            conn.close()
        return UserTable.to_self(user)

    @staticmethod
    def get_user_by_email(email: str) -> UserTable:
        query = f"""SELECT * FROM carmate.{UserRepository.POSTGRES_TABLE_NAME} 
                    WHERE email_address=%s"""

        conn: Any
        user_data: tuple
        try:
            conn = establishing_connection()
        except Exception as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                curs.execute(query, (email,))
                user_data = curs.fetchone()

            conn.close()
            if not user_data:
                raise NotFound("user not found")
        return UserTable.to_self(user_data)

    @staticmethod
    def get_user_by_id(id: int) -> UserTable:
        query = f"""SELECT * FROM carmate.{UserRepository.POSTGRES_TABLE_NAME} 
                    WHERE id=%s"""

        conn: Any
        user_data: tuple
        try:
            conn = establishing_connection()
        except Exception as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (id,))
                    user_data = curs.fetchone()
                except ProgrammingError:
                    raise NotFound("user not found")
                except Exception as e:
                    raise InternalServer(str(e))
            conn.close()

        if user_data is None:
            raise NotFound("user not found")
        return UserTable.to_self(user_data)
