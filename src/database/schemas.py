from ast import List
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class UserTable:
    id: int
    first_name: str
    last_name: str
    email_address: str
    password: bytes
    account_status: str
    created_at: datetime
    profile_picture: Optional[bytes] = None

    @staticmethod
    def to_self(_tuple: tuple):
        return UserTable(
            _tuple[0],
            _tuple[1],
            _tuple[2],
            _tuple[3],
            _tuple[4],
            _tuple[5],
            _tuple[6],
            _tuple[7]
        )


@dataclass(frozen=True)
class TokenTable:
    token: bytes
    expiration: datetime
    user: int

    @staticmethod
    def to_self(_tuple: tuple):
        return TokenTable(
            _tuple[0],
            _tuple[1],
            _tuple[2],
        )


@dataclass
class LicenseTable:
    id: int
    license_img: bytes
    document_type: str
    validation_status: str
    created_at: datetime
    user_id: int

    @staticmethod
    def to_self(_tuple: tuple):
        return LicenseTable(
            _tuple[0],
            _tuple[1],
            _tuple[2],
            _tuple[3],
            _tuple[4],
            _tuple[5],
        )


@dataclass
class DriverProfileTable:
    id: int
    description: str
    created_at: datetime
    user_id: int

    @staticmethod
    def to_self(_tuple: tuple):
        return DriverProfileTable(
            _tuple[0],
            _tuple[1],
            _tuple[2],
            _tuple[3]
        )


@dataclass
class PassengerProfileTable:
    id: int
    description: str
    created_at: datetime
    user_id: int

    @staticmethod
    def to_self(_tuple: tuple):
        return PassengerProfileTable(
            _tuple[0],
            _tuple[1],
            _tuple[2],
            _tuple[3]
        )


@dataclass
class ReserveCarpoolingTable:
    user_id: int
    carpooling_id: int
    passenger_code: int
    passenger_code_validated: bool = False
    passenger_code_date_validated: datetime = None
    canceled: bool = False

    @staticmethod
    def to_self(*args, **kwargs):
        if len(args) != 3:
            raise ValueError("to_self() requires exactly 3 positional arguments")

        user_id, carpooling_id, passenger_code = args
        return ReserveCarpoolingTable(
            user_id,
            carpooling_id,
            passenger_code,
            kwargs.get('passenger_code_validated', False),
            kwargs.get('passenger_code_date_validated', None),
            kwargs.get('canceled', False)
        )


@dataclass
class CarpoolingTable:
    id: int
    starting_point: List[float]
    destination: List[float]
    max_passengers: int
    price: float
    is_canceled: bool
    departure_date_time: datetime
    driver_id: int

    @staticmethod
    def to_self(*args):
        if len(args) != 8:
            raise ValueError("to_self() requires exactly 8 positional arguments")
        return CarpoolingTable(
            args[0],
            args[1],
            args[2],
            args[3],
            args[4],
            args[5],
            args[6],
            args[7]
        )
