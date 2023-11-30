from typing import List

from database.repositories.user_admin_repository import UserAdminRepositoryInterface


class InMemoryUserAdminRepository(UserAdminRepositoryInterface):
    def __init__(self):
        self.admin_users: List[int] = [1]

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_users
