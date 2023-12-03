from hashlib import sha512

from api.worker.user.models import PassengerProfileDTO
from api.exceptions import (
    PassengerNotFound,
    InternalServerError
)
from database.exceptions import NotFound
from database.schemas import DriverProfileTable
from database.repositories import (
    TokenRepositoryInterface, 
    PassengerProfileRepositoryInterface
)


class GetPassengerProfile:
    token_repository: TokenRepositoryInterface
    passenger_profile_repository: PassengerProfileRepositoryInterface

    def __init__(self,
                 token_repository: TokenRepositoryInterface,
                 passenger_profile_repository: PassengerProfileRepositoryInterface) -> None:
        self.token_repository = token_repository
        self.passenger_profile_repository = passenger_profile_repository

    def worker(self,
               passenger_id: int=None,
               token: str=None) -> PassengerProfileDTO:
        passenger_profile: DriverProfileTable = None
        if token is not None:
            try:
                user = self.token_repository.get_user(sha512(token.encode()).digest())
                passenger_profile = self.passenger_profile_repository.get_passenger_by_user_id(user.id)
            except NotFound:
                raise PassengerNotFound()
            except Exception as e:
                raise InternalServerError(str(e))
        elif passenger_id is not None:
            try:
                passenger_profile = self.passenger_profile_repository.get_passenger(passenger_id)
            except NotFound:
                raise PassengerNotFound()
            except Exception as e:
                raise InternalServerError(str(e))
        else:
            raise PassengerNotFound()
        return PassengerProfileDTO(passenger_profile.description, passenger_profile.created_at)
