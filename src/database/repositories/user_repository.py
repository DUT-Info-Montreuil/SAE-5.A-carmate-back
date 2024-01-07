from psycopg2 import ProgrammingError, errorcodes
from psycopg2.errors import lookup

from api import hash
from api.worker.auth.models import CredentialDTO
from api.worker.user import AccountStatus
from database import USER_TABLE_NAME, establishing_connection
from database.interfaces import UserRepositoryInterface
from database.exceptions import InternalServer, UniqueViolation, NotFound
from database.schemas import UserTable


class UserRepository(UserRepositoryInterface):
    def insert(self,
               credential: CredentialDTO, 
               account_status: AccountStatus) -> UserTable:
        first_name, last_name, email_address, password = credential.to_json().values()
        query: str = f"""
            INSERT INTO carmate.{USER_TABLE_NAME}(first_name, last_name, email_address, password, account_status)
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id, first_name, last_name, email_address, password, account_status, created_at, profile_picture
        """

        user: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (first_name, last_name,
                                         email_address, hash(password), account_status.name,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                user = curs.fetchone()
        return UserTable(*user)

    def get_user_by_email(self,
                          email: str) -> UserTable:
        query = f"""
            SELECT * FROM carmate.{USER_TABLE_NAME} 
            WHERE email_address=%s
        """

        user_data: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (email,))
                except ProgrammingError:
                    raise NotFound("user not found")
                except Exception as e:
                    raise InternalServer(str(e))
                user_data = curs.fetchone()

        if not user_data:
            raise NotFound("user not found")
        return UserTable(*user_data)

    @staticmethod
    def get_user_by_id(id: int) -> UserTable:
        query = f"""SELECT * FROM carmate.{USER_TABLE_NAME} 
                    WHERE id=%s"""

        user_data: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (id,))
                except ProgrammingError:
                    raise NotFound("user not found")
                except Exception as e:
                    raise InternalServer(str(e))
                user_data = curs.fetchone()

        if user_data is None:
            raise NotFound("user not found")
        return UserTable.to_self(user_data)

    def get_user_by_id(self,
                       id: int) -> UserTable:
        query = f"""
            SELECT * FROM carmate.{USER_TABLE_NAME} 
            WHERE id=%s
        """

        user_data: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (id,))
                except ProgrammingError:
                    raise NotFound("user not found")
                except Exception as e:
                    raise InternalServer(str(e))
                user_data = curs.fetchone()

        if user_data is None:
            raise NotFound("user not found")
        return UserTable(*user_data)
