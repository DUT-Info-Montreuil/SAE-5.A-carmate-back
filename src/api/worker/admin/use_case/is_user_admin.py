from hashlib import sha512
from typing import List, Dict, Union

from database.repositories import TokenRepositoryInterface
from database.repositories.user_admin_repository import UserAdminRepositoryInterface


class IsUserAdmin:

    def __init__(self, token_repository: TokenRepositoryInterface, user_admin_repository: UserAdminRepositoryInterface):
        self.token_repository = token_repository
        self.user_admin_repository = user_admin_repository

    def worker(self, token: str) -> bool:
        if token is None:
            raise ValueError()

        user = self.token_repository.get_user(sha512(token.encode()).digest())
        user_is_admin = self.user_admin_repository.is_admin(user.id)
        return user_is_admin
