from typing import List

from psycopg2 import ProgrammingError

from database import USER_BANNED_TABLE_NAME, establishing_connection
from database.interfaces import UserBannedRepositoryInterface
from database.exceptions import InternalServer, NotFound


class UserBannedRepository(UserBannedRepositoryInterface):
    def __init__(self):
        self.banned_users: List[int] = [2]

    def is_banned(self, 
                  user_id: int) -> bool:
        query = f"""
            SELECT EXISTS (
                SELECT 1 
                FROM carmate.{USER_BANNED_TABLE_NAME}
                WHERE user_id = %s
            ) as is_banned
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
