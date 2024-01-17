from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List

from api.worker.user.models import PassengerProfileDTO


@dataclass
class PublishedCarpoolingDTO:
    id: int
    starting_point: List[float]
    destination: List[float]
    max_passengers: int
    price: float
    is_canceled: bool
    departure_date_time: datetime
    driver_id: int
    seats_taken: int
    passengers_profile: List[PassengerProfileDTO]

    def to_json(self):
        return asdict(self)
