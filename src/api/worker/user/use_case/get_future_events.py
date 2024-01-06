from hashlib import sha512
from typing import List

from api.worker import Worker, FutureReservationDTO, FutureCarpoolingDTO
from api.worker.user.models.future_events_dto import FutureEventsDTO
from database.exceptions import NotFound
from database.schemas import DriverProfileTable, UserTable


class GetFutureEvents(Worker):
    def worker(self, token: str):
        user: UserTable = None
        driver_profile: DriverProfileTable = None
        future_reservations: List[FutureReservationDTO] = []
        future_carpoolings: List[FutureCarpoolingDTO] = []

        user = self.token_repository.get_user(sha512(token.encode()).digest())

        try:
            driver_profile = self.token_repository.get_driver_profile(sha512(token.encode()).digest())
        except NotFound:
            pass

        future_reservations = self.booking_carpooling_repository.get_future_reservations_by_passenger_id(user.id)

        if driver_profile is not None:
            future_carpoolings = self.carpooling_repository.get_future_carpoolings_by_driver_id(driver_profile.id)

        return FutureEventsDTO(future_reservations, future_carpoolings)
