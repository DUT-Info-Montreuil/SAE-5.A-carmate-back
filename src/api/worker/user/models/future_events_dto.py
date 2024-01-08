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


@dataclass()
class FutureCarpoolingDTO:
    carpooling_id: int
    departure_date_time: datetime
    destination: List[float]
    starting_point: List[float]
    max_passengers: int
    seats_taken: int

    def to_json(self):
        return {
            "carpooling_id": self.carpooling_id,
            "departure_date_time": self.departure_date_time,
            "destination": self.destination,
            "starting_point": self.starting_point,
            "max_passengers": self.max_passengers,
            "seats_taken": self.seats_taken
        }


@dataclass()
class FutureEventsDTO:
    reserved: List[FutureReservationDTO]
    proposed: List[FutureCarpoolingDTO]

    def to_json(self):
        return asdict(self)
