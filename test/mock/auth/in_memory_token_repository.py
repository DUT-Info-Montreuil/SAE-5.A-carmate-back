from datetime import datetime
from typing import List

from database.repositories import TokenRepositoryInterface
from database.schemas import TokenTable, UserTable


class InMemoryTokenRepository(TokenRepositoryInterface):
    tokens: List[TokenTable] = []

    @staticmethod
    def insert(token: str, expiration: datetime, user: UserTable) -> TokenTable:
        in_memory_token = TokenTable.to_self((token, expiration, user.id))
        InMemoryTokenRepository.tokens.append(in_memory_token)
        return in_memory_token
