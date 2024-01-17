from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BookedCarpoolingDTO:
    user_id: int
    carpooling_id: int
    passenger_code: int
    passenger_code_validated: bool = False
    passenger_code_date_validated: datetime = None
    canceled: bool = False

    def to_json(self):
        return asdict(self)
