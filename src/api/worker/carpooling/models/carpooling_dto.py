from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from database.schemas import CarpoolingTable


@dataclass
class CarpoolingDTO:
    starting_point: List[float]
    destination: List[float]
    max_passagers: int
    price: float
    is_canceled: bool
    departure_date_time: datetime
    driver_id: int

    @staticmethod
    def from_table(table: CarpoolingTable):
        return CarpoolingDTO(
            table.starting_point,
            table.destination,
            table.max_passagers,
            table.price,
            table.is_canceled,
            table.departure_date_time,
            table.driver_id
        )

    def to_json(self):
        return asdict(self)
