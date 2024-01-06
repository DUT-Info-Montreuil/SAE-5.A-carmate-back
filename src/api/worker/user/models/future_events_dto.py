from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List


@dataclass
class FutureReservationDTO:
    passenger_code: int
    driver_id: int
    departure_date_time: datetime
    destination: str
    starting_point: str
    carpooling_id: int

    def to_json(self):
        return asdict(self)


@dataclass
class FutureCarpoolingDTO:
    carpooling_id: int
    departure_date_time: datetime
    destination: List[float]
    starting_point: List[float]
    max_passengers: int
    seats_taken: int

    def to_json(self):
        return asdict(self)


@dataclass
class FutureEventsDTO:
    reserved: List[FutureReservationDTO]
    proposed: List[FutureCarpoolingDTO]

    def to_json(self):
        return asdict(self)
