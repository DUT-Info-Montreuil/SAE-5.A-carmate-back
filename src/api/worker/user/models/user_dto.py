from dataclasses import dataclass
from typing import Optional


@dataclass
class UserDTO(frozen=True):
    id: int
    first_name: str
    last_name: str
    email_address: str
    password: bytes
    profile_picture: Optional[bytes] = None
