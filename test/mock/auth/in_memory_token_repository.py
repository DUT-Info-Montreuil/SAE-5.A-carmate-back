import secrets

from hashlib import sha512
from datetime import datetime, timedelta
from typing import List

from database.repositories import TokenRepositoryInterface
from database.schemas import TokenTable, UserTable
from database.exceptions import *


class InMemoryTokenRepository(TokenRepositoryInterface):
    tokens: List[TokenTable] = [
        TokenTable(sha512("token-valid".encode()).digest(), datetime.now() + timedelta(days=1), 1),
        TokenTable(sha512("token-invalid".encode()).digest(), datetime.now() - timedelta(days=15), 1)
    ]

    @staticmethod
    def insert(token: str, expiration: datetime, user: UserTable) -> TokenTable:
        in_memory_token = TokenTable.to_self((token, expiration, user.id))
        InMemoryTokenRepository.tokens.append(in_memory_token)
        return in_memory_token

    @staticmethod
    def get_expiration(token_hashed: str) -> datetime:
        token_found: TokenTable = None
        for token in InMemoryTokenRepository.tokens:
            if secrets.compare_digest(bytes.fromhex(token_hashed), token.token):
                token_found = token
        
        if not token_found:
            raise NotFound("token not found")
        return token_found.expiration
