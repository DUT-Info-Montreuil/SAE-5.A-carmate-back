from abc import ABC
from typing import Any, List

from database import establishing_connection
from database.exceptions import InternalServer


class UserBannedRepositoryInterface(ABC):
    def is_banned(self,
                  user_id: int): ...


class UserBannedRepository(UserBannedRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "user_banned"

    def __init__(self):
        self.banned_users: List[int] = [2]

    def is_banned(self, 
                  user_id: int) -> bool:
        query = f"""SELECT EXISTS (
                SELECT 1 
                FROM carmate.{UserBannedRepository.POSTGRES_TABLE_NAME}
                WHERE user_id = %s
            ) as is_banned"""

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
