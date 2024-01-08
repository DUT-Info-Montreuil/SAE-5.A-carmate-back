from abc import ABC

from database.schemas import PassengerProfileTable, UserTable


class PassengerProfileRepositoryInterface(ABC):
    def insert(self,
               user: UserTable) -> PassengerProfileTable: ...

    def get_passenger_by_user_id(self,
                                 user_id: int) -> PassengerProfileTable: ...

    def get_passenger(self,
                      passenger_id: int) -> PassengerProfileTable: ...
