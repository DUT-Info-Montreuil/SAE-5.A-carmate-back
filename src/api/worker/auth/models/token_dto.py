from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TokenDTO:
    token: bytes
    expire_at: datetime
    user_id: int
