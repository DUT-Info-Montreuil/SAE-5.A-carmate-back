from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


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
