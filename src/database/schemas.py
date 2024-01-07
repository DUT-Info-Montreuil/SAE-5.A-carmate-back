from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class Weekday(Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7


class DatabaseTable:
    """
    Representation of a table in database
    """
    pass


@dataclass
class UserTable(DatabaseTable):
    id: int
    first_name: str
    last_name: str
    email_address: str
    password: bytes
    account_status: str
    created_at: datetime
    profile_picture: Optional[bytes] = None


@dataclass(frozen=True)
class TokenTable(DatabaseTable):
    token: bytes
    expiration: datetime
    user: int


@dataclass
class LicenseTable(DatabaseTable):
    id: int
    license_img: bytes
    document_type: str
    validation_status: str
    created_at: datetime
    user_id: int


@dataclass
class DriverProfileTable(DatabaseTable):
    id: int
    description: str
    created_at: datetime
    user_id: int


@dataclass
class PassengerProfileTable(DatabaseTable):
    id: int
    description: str
    created_at: datetime
    user_id: int


@dataclass
class ReserveCarpoolingTable(DatabaseTable):
    user_id: int
    carpooling_id: int
    passenger_code: int
    passenger_code_validated: bool = False
    passenger_code_date_validated: datetime = None
    canceled: bool = False


@dataclass
class CarpoolingTable(DatabaseTable):
    id: int
    starting_point: List[float]
    destination: List[float]
    max_passengers: int
    price: float
    is_canceled: bool
    departure_date_time: datetime
    driver_id: int


@dataclass
class ReviewTable:
    user_id: int
    driver_id: int
    economic_driving_rating: float
    safe_driving_rating: float
    sociability_rating: float
    review: str
    rating_date: datetime
    updated_rating_date: datetime


@dataclass
class PassengerScheduledCarpoolingTable(DatabaseTable):
    id: int
    label: str
    starting_point: List[float]
    destination: List[float]
    start_date: datetime.date
    end_date: datetime.date
    start_hour: datetime.time
    days: List[Weekday]
    passenger_id: int
