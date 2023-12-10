from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class DriverProfileDTO:
    description: str
    created_at: datetime

    @staticmethod
    def to_self(_tuple: tuple):
        return DriverProfileDTO(
            _tuple[0],
            _tuple[1],
            _tuple[2]
        )
    
    def to_json(self):
        return asdict(self)
