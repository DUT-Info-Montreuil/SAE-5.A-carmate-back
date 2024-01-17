from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from database.schemas import Weekday


@dataclass
class ProposeScheduledCarpoolingDTO:
    id: int
    label: str
    starting_point: List[float]
    destination: List[float]
    start_date: datetime.date
    end_date: datetime.date
    start_hour: datetime.time
    days: List[Weekday]
    passenger_id: int
    carpoolings: List[tuple]
    def to_json(self):
        return asdict(self)