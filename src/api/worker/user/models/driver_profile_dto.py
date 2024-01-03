from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

from database.schemas import DriverProfileTable


@dataclass
class DriverProfileDTO:
    id: int
    description: str
    created_at: datetime
    user_id: int
    profile_picture: Optional[bytes] | None = None
    
    @staticmethod
    def from_table(table: DriverProfileTable) -> DriverProfileDTO:
        return DriverProfileDTO(
            table.id,
            table.description,
            table.created_at,
            table.user_id
        )
    

    def set_profile_picture(self,
                            new_profile_picture: bytes | None) -> DriverProfileDTO:
        self.profile_picture = new_profile_picture
        return self
    
    def to_json(self):
        return asdict(self)
