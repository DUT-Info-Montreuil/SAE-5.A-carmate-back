from abc import ABC
from typing import Any

from database import establishing_connection, InternalServer


class UserAdminRepositoryInterface(ABC):
    @staticmethod
    def is_admin(user_id: int) -> bool: ...


class UserAdminRepository(UserAdminRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "user_admin"
    @staticmethod
    def is_admin(user_id: int) -> bool:
        query = f"""SELECT EXISTS (
                        SELECT 1 
                        FROM carmate.{UserAdminRepository.POSTGRES_TABLE_NAME}
                        WHERE "user" = %s
                    ) as is_admin"""

        conn: Any
        user_data: tuple
        try:
            conn = establishing_connection()
        except Exception as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                curs.execute(query, (user_id, ))
                user_data = curs.fetchone()[0]

            conn.close()
            if not user_data:
                return False
        return True
