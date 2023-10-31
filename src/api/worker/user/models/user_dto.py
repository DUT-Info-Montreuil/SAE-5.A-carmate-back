from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class UserDTO:
    id: int
    first_name: str
    last_name: str
    email_address: str
    password: bytes
    profile_picture: Optional[bytes] = field(init=None)

    def to_json(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email_address": self.email_address,
            "password": self.password,
            "profile_picture": self.profile_picture
        }
