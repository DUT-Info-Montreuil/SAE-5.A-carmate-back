from abc import ABC
from typing import List

from database.interfaces import UserBannedRepositoryInterface


class InMemoryUserBannedRepository(UserBannedRepositoryInterface):
    def __init__(self):
        self.banned_users: List[int] = [2]

    def is_banned(self, 
                  user_id: int) -> bool:
        return user_id in self.banned_users
