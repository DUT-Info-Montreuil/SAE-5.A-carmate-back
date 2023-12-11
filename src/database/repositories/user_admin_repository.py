from abc import ABC

from database import establishing_connection


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
                        WHERE user_id=%s
                    ) as is_admin"""

        user_data: tuple
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                curs.execute(query, (user_id, ))
                user_data = curs.fetchone()[0]

        if not user_data:
            return False
        return True
