from abc import ABC
from typing import Tuple

from database.schemas import DriverProfileTable, UserTable


class DriverProfileRepositoryInterface(ABC):
    def insert(self,
               user: UserTable) -> DriverProfileTable: ...

    def get_driver_by_user_id(self,
                              user_id: int) -> Tuple[DriverProfileTable, 
                                                     bytes | None]: ...

    def get_driver(self,
                   driver_id: int) -> Tuple[DriverProfileTable,
                                            bytes | None]: ...
