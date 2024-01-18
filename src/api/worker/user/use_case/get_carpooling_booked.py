from hashlib import sha512
from typing import List

from api.worker import Worker
from api.worker.carpooling.models import CarpoolingForRecap, CarpoolingForRecapWithPassengerCode
from api.worker.user.models import BookedCarpoolingDTO
from api.exceptions import InternalServerError
from database.schemas import ReserveCarpoolingTable, UserTable


class GetBookedCarpoolings(Worker):
    def worker(self,
               token: str) -> List[CarpoolingForRecapWithPassengerCode]:
        user: UserTable
        try:
            user = self.token_repository.get_user(sha512(token.encode()).digest())
        except Exception as e:
            raise InternalServerError(str(e))

        booked_carpoolings: List[CarpoolingForRecapWithPassengerCode]
        try:
            booked_carpoolings = [CarpoolingForRecapWithPassengerCode(*carpooling) for carpooling in self.booking_carpooling_repository.get_booked_carpoolings(user.id)]
        except Exception as e:
            raise InternalServerError(str(e))
        return booked_carpoolings
