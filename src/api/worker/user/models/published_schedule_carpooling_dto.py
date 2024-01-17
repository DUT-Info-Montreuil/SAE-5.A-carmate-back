from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from database.schemas import Weekday


@dataclass
class PublishedScheduleCarpoolingDTO:
    id: int
    label: str
    starting_point: List[float]
    destination: List[float]
    start_hour: datetime.time
    start_date: datetime.date
    end_date: datetime.date
    days: List[Weekday]
    max_passengers: int
    driver_id: int

    def to_json(self):
        return asdict(self)
