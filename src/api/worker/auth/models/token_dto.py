from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TokenDTO:
    token: str
    expire_at: datetime
    user_id: int

    def to_json(self) -> dict:
        return {
            "token": self.token,
            "expire_at": self.expire_at,
            "user_id": self.user_id
        }
