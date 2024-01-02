from abc import ABC
from datetime import datetime
from typing import List

from database.schemas import PassengerScheduledCarpoolingTable, CarpoolingTable


class ProposeScheduledCarpoolingRepositoryInterface(ABC):
    def insert(self,
               data: PassengerScheduledCarpoolingTable) -> int: ...

    def has_same_time_proposed_scheduled_carpooling(self,
                                                    data: PassengerScheduledCarpoolingTable) -> bool: ...

    def get_carpoolings_to_reserve_for(self, propose_scheduled_carpooling_id: int) -> List[CarpoolingTable]: ...

    def get_user_id_from_scheduled_carpooling(self, propose_scheduled_carpooling_id: int) -> int: ...

    def get_matching_proposed_scheduled_carpooling(self,
                                                   starting_point: List[float],
                                                   destination: List[float],
                                                   date: datetime.date,
                                                   time: datetime.time,
                                                   limit: int) -> List[int]: ...
