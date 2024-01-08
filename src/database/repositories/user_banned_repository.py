from abc import ABC
from typing import List

from psycopg2 import ProgrammingError

from database import establishing_connection
from database.exceptions import InternalServer, NotFound
from database.repositories import user_banned_table_name


class UserBannedRepositoryInterface(ABC):
    def is_banned(self,
                  user_id: int): ...


class UserBannedRepository(UserBannedRepositoryInterface):
    def __init__(self):
        self.banned_users: List[int] = [2]

    def is_banned(self, 
                  user_id: int) -> bool:
        query = f"""
            SELECT EXISTS (
                SELECT 1 
                FROM carmate.{user_banned_table_name}
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
