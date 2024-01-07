from abc import ABC
from datetime import datetime

from database.schemas import (
    DriverProfileTable,
    TokenTable,
    UserTable
)


class TokenRepositoryInterface(ABC):
    def insert(self,
               token: str,
               expiration: datetime,
               user: UserTable) -> TokenTable: ...

    def get_expiration(self,
                       token_hashed: bytes) -> datetime: ...

    def get_user(self,
                 token: bytes) -> UserTable: ...

    def get_driver_profile(self,
                           token: bytes) -> DriverProfileTable: ...

    def get_passenger_profile(self,
                              token: bytes) -> DriverProfileTable: ...
