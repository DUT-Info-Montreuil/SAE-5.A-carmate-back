import base64

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class UserDTO:
    first_name: str
    last_name: str
    email_address: str
    created_at: datetime
    profile_picture: Optional[str] = None

    def to_json(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email_address": self.email_address,
            "created_at": self.created_at,
            "profile_picture": self.profile_picture if self.profile_picture is None else base64.b64encode(self.profile_picture).decode()
        }
