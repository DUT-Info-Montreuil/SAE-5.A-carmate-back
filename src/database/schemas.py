from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self


@dataclass(frozen=True)
class UserTable:
    id: int
    first_name: str
    last_name: str
    email_address: str
    password: bytes
    profile_picture: Optional[bytes] = None

    @staticmethod
    def to_self(_tuple: tuple) -> Self:
        return UserTable(
            _tuple[0],
            _tuple[1],
            _tuple[2],
            _tuple[3],
            _tuple[4]
        )


@dataclass(frozen=True)
class TokenTable:
    token: bytes
    expiration: datetime
    user: int

    @staticmethod
    def to_self(_tuple: tuple) -> Self:
        return TokenTable(
            _tuple[0],
            _tuple[1],
            _tuple[2],
        )
