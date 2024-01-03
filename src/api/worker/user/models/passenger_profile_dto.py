from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

from database.schemas import PassengerProfileTable


@dataclass
class PassengerProfileDTO:
    description: str
    created_at: datetime
    profile_picture: Optional[bytes] | None = None

    @staticmethod
    def from_table(table: PassengerProfileTable) -> PassengerProfileDTO:
        return PassengerProfileDTO(
            table.description,
            table.created_at
        )
    
    def set_profile_picture(self,
                            new_profile_picture: bytes | None) -> PassengerProfileDTO:
        self.profile_picture = new_profile_picture
        return self

    def to_json(self):
        return asdict(self)
