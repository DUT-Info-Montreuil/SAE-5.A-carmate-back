import secrets

from hashlib import sha512
from datetime import datetime, timedelta
from typing import List

from database.repositories import TokenRepositoryInterface
from database.schemas import TokenTable, UserTable
from database.exceptions import *


class InMemoryTokenRepository(TokenRepositoryInterface):
    def __init__(self, user_repo=None):
        self.tokens: List[TokenTable] = [
            TokenTable(sha512("token-valid".encode()).digest(), datetime.now() + timedelta(days=1), 1),
            TokenTable(sha512("token-invalid".encode()).digest(), datetime.now() - timedelta(days=15), 1)
        ]
        self.user_repo = user_repo

    def insert(self,token: str, expiration: datetime, user: UserTable) -> TokenTable:
        in_memory_token = TokenTable.to_self((token, expiration, user.id))
        self.tokens.append(in_memory_token)
        return in_memory_token

    def get_expiration(self, token_hashed: str) -> datetime:
        token_found: TokenTable = None
        for token in self.tokens:
            if secrets.compare_digest(bytes.fromhex(token_hashed), token.token):
                token_found = token
        
        if not token_found:
            raise NotFound("token not found")
        return token_found.expiration

    def get_user(self, token: str) -> UserTable:
        if self.user_repo is None:
            raise Exception("The function get user won't work without a user repository")

        found_token: TokenTable | None = None
        found_user: UserTable | None = None

        for db_token in self.tokens:
            if secrets.compare_digest(sha512(token.encode()).digest(), db_token.token):
                found_token = db_token

        if found_token is None:
            raise NotFound("token not found")

        for db_user in self.user_repo.users:
            if db_user.id == found_token.user:
                found_user = db_user

        if found_user is None:
            raise Exception("the token is linked to no user, this shouldn't happen")

        return found_user
