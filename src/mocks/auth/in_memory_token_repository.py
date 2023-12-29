import secrets

from hashlib import sha512
from datetime import datetime, timedelta
from typing import List

from database.repositories import TokenRepositoryInterface
from database.schemas import TokenTable, UserTable, DriverProfileTable
from database.exceptions import *


class InMemoryTokenRepository(TokenRepositoryInterface):
    def __init__(self, 
                 user_repository, 
                 driver_repository):
        self.tokens: List[TokenTable] = [
            TokenTable(sha512("token-user-valid".encode()).digest(), datetime.now() + timedelta(days=1), 0),
            TokenTable(sha512("token-admin-valid".encode()).digest(), datetime.now() + timedelta(days=1), 1),
            TokenTable(sha512("token-user-invalid".encode()).digest(), datetime.now() - timedelta(days=15), 2)
        ]
        self.user_repository = user_repository
        self.driver_repository = driver_repository

    def insert(self,token: str, expiration: datetime, user: UserTable) -> TokenTable:
        in_memory_token = TokenTable(token, expiration, user.id)
        self.tokens.append(in_memory_token)
        return in_memory_token

    def get_expiration(self, token_hashed: bytes) -> datetime:
        token_found: TokenTable = None
        for token in self.tokens:
            if secrets.compare_digest(token_hashed, token.token):
                token_found = token
        
        if not token_found:
            raise NotFound("token not found")
        return token_found.expiration

    def get_user(self, token: str) -> UserTable:
        found_token: TokenTable | None = None
        found_user: UserTable | None = None

        for db_token in self.tokens:
            if secrets.compare_digest(token, db_token.token):
                found_token = db_token

        if found_token is None:
            raise NotFound("token not found")

        for db_user in self.user_repository.users:
            if db_user.id == found_token.user:
                found_user = db_user

        if found_user is None:
            raise Exception("the token is linked to no user, this shouldn't happen")

        return found_user

    def get_driver_profile(self, token: bytes) -> DriverProfileTable:
        found_token: TokenTable | None = None
        found_user: UserTable | None = None
        found_driver: DriverProfileTable | None = None

        for db_token in self.tokens:
            if secrets.compare_digest(token, db_token.token):
                found_token = db_token
                break

        if found_token is None:
            raise NotFound("token not found")

        for user in self.user_repository.users:
            if found_token.user == user.id:
                found_user = user
                break

        if found_user is None:
            raise Exception("the token is linked to no user, this shouldn't happen")

        for driver in self.driver_repository.driver_profiles:
            if driver.user_id == found_user.id:
                found_driver = driver
                break

        if found_driver is None:
            raise NotFound("driver not found")

        return found_driver
