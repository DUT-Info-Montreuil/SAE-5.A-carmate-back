from psycopg2 import ProgrammingError

from database import USER_ADMIN_TABLE_NAME, establishing_connection
from database.interfaces import UserAdminRepositoryInterface
from database.exceptions import InternalServer, NotFound


class UserAdminRepository(UserAdminRepositoryInterface):
    def is_admin(self,
                 user_id: int) -> bool:
        query = f"""
            SELECT EXISTS (
                SELECT 1 
                FROM carmate.{USER_ADMIN_TABLE_NAME}
                WHERE user_id=%s
            ) AS is_admin
        """

        user_data: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (user_id,))
                except ProgrammingError:
                    raise NotFound("user not found")
                except Exception as e:
                    raise InternalServer(str(e))
                user_data = curs.fetchone()[0]
        return user_data is not None and bool(user_data)
