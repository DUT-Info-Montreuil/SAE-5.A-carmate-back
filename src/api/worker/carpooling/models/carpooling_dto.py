from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from database.schemas import CarpoolingTable


@dataclass
class CarpoolingDTO:
    starting_point: List[float]
    destination: List[float]
    max_passengers: int
    price: float
    is_canceled: bool
    departure_date_time: datetime
    driver_id: int

    @staticmethod
    def from_table(table: CarpoolingTable):
        return CarpoolingDTO(
            table.starting_point,
            table.destination,
            table.max_passengers,
            table.price,
            table.is_canceled,
            table.departure_date_time,
            table.driver_id
        )

    def to_json(self):
        return asdict(self)


@dataclass
class CarpoolingForRecap:
    id: int
    starting_point: List[float]
    destination: List[float]
    max_passengers: int
    price: float
    departure_date_time: datetime
    driver_id: int
    seats_taken: int
    is_scheduled: bool

    @staticmethod
    def to_self(_tuple: tuple):
        return CarpoolingForRecap(
            _tuple[0],
            _tuple[1],
            _tuple[2],
            _tuple[3],
            _tuple[4],
            _tuple[5],
            _tuple[6],
            _tuple[7],
            _tuple[8],
            _tuple[9],
            _tuple[10]
        )

    def to_json(self):
        return asdict(self)

@dataclass
class CarpoolingForRecapWithPassengerCode(CarpoolingForRecap):
    passenger_code: str

    def to_json(self):
        return asdict(self)

@dataclass
class CarpoolingForRecapWithFirstAndLastName(CarpoolingForRecap):
    first_name: str
    last_name: str

    def to_json(self):
        return asdict(self)