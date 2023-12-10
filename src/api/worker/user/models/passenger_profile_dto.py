from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PassengerProfileDTO:
    description: str
    created_at: datetime

    @staticmethod
    def to_self(_tuple: tuple):
        return PassengerProfileDTO(
            _tuple[0],
            _tuple[1]
        )
    
    def to_json(self):
        return asdict(self)
