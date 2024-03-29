from datetime import datetime
from typing import List

from database.interfaces import PassengerProfileRepositoryInterface, UserRepositoryInterface
from database.exceptions import (
    NotFound,
    UniqueViolation
)
from database.schemas import (
    PassengerProfileTable,
    UserTable
)


class InMemoryPassengerProfileRepository(PassengerProfileRepositoryInterface):
    user_repository: UserRepositoryInterface
    
    def __init__(self,
                 user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

        self.passenger_profile_count = 0
        self.passenger_profiles: List[PassengerProfileTable] = [
            PassengerProfileTable(0, ' ', datetime.now(), 0),
            PassengerProfileTable(1, ' ', datetime.now(), 1),
            PassengerProfileTable(2, ' ', datetime.now(), 2),
            PassengerProfileTable(3, ' ', datetime.now(), 3),
        ]

    def insert(self,
               user: UserTable) -> PassengerProfileTable:
        for passenger in self.passenger_profiles:
            if passenger.user_id == user.id:
                raise UniqueViolation("passenger profile already exist")

        in_memory_passenger_profile = PassengerProfileTable(
            self.passenger_profile_count, ' ', datetime.now(), user.id)

        self.passenger_profiles.append(in_memory_passenger_profile)
        self.passenger_profile_count = self.passenger_profile_count + 1
        return in_memory_passenger_profile

    def get_passenger_by_user_id(self,
                                 user_id: int) -> PassengerProfileTable:
        for passenger in self.passenger_profiles:
            if passenger.user_id == user_id:
                profile_picture: bytes | None = self.user_repository.get_user_by_id(passenger.user_id).profile_picture
                return passenger, profile_picture
        raise NotFound("Passenger not found")

    def get_passenger(self,
                      passenger_id: int) -> PassengerProfileTable:
        for passenger in self.passenger_profiles:
            if passenger.id == passenger_id:
                profile_picture: bytes | None = self.user_repository.get_user_by_id(passenger.user_id).profile_picture
                return passenger, profile_picture
        raise NotFound("Passenger not found")
