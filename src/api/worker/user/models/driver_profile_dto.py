from dataclasses import dataclass, asdict
from datetime import datetime

from database.schemas import DriverProfileTable


@dataclass
class DriverProfileDTO:
    id: int
    description: str
    created_at: datetime
    user_id: int

    @staticmethod
    def from_table(table: DriverProfileTable):
        return DriverProfileDTO(
            table.id,
            table.description,
            table.created_at,
            table.user_id
        )

    @staticmethod
    def to_self(_tuple: tuple):
        return DriverProfileDTO(
            _tuple[0],
            _tuple[1],
            _tuple[2]
        )
    
    def to_json(self):
        return asdict(self)
