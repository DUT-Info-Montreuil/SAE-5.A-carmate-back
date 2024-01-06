from hashlib import sha512
from typing import List

from api.worker import Worker, FutureCarpoolingDTO
from api.worker.user.models import FutureEventsDTO
from database.exceptions import NotFound
from database.schemas import DriverProfileTable, UserTable


class GetFutureEvents(Worker):
    def worker(self, 
               token: str):
        user = self.token_repository.get_user(sha512(token.encode()).digest())
        future_reservations = self.booking_carpooling_repository.get_future_reservations_by_passenger_id(user.id)
        
        driver_profile: DriverProfileTable
        future_carpoolings: List[FutureCarpoolingDTO]
        try:
            driver_profile = self.token_repository.get_driver_profile(sha512(token.encode()).digest())
            future_carpoolings = self.carpooling_repository.get_future_carpoolings_by_driver_id(driver_profile.id)
        except NotFound:
            future_carpoolings = []
        return FutureEventsDTO(future_reservations, future_carpoolings)
