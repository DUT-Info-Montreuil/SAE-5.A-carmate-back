from hashlib import sha512

from api.worker import Worker
from api.worker.user.models import PassengerProfileDTO
from api.exceptions import (
    PassengerNotFound,
    InternalServerError
)
from database.schemas import DriverProfileTable
from database.exceptions import NotFound


class GetPassengerProfile(Worker):
    def worker(self,
               passenger_id: int=None,
               token: str=None) -> PassengerProfileDTO:
        passenger_profile: DriverProfileTable
        picture_profile: bytes | None
        if token is not None:
            try:
                user = self.token_repository.get_user(sha512(token.encode()).digest())
                passenger_profile, picture_profile = self.passenger_profile_repository.get_passenger_by_user_id(user.id)
            except NotFound:
                raise PassengerNotFound()
            except Exception as e:
                raise InternalServerError(str(e))
        elif passenger_id is not None:
            try:
                passenger_profile, picture_profile = self.passenger_profile_repository.get_passenger(passenger_id)
            except NotFound:
                raise PassengerNotFound()
            except Exception as e:
                raise InternalServerError(str(e))
        else:
            raise PassengerNotFound()
        return PassengerProfileDTO.from_table(passenger_profile).set_profile_picture(picture_profile)
