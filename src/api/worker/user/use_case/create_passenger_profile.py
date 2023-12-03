from hashlib import sha512

from api.exceptions import (
    InternalServerError,
    ProfileAlreadyExist,
    UserNotFound
)
from database.schemas import UserTable
from database.exceptions import (
    NotFound,
    UniqueViolation
)
from database.repositories import (
    TokenRepositoryInterface,
    PassengerProfileRepositoryInterface
)


class CreatePassengerProfile:
    token_repository: TokenRepositoryInterface
    passenger_profile_repository: PassengerProfileRepositoryInterface

    def __init__(self,
                 token_repository: TokenRepositoryInterface,
                 passenger_profile_repository: PassengerProfileRepositoryInterface) -> None:
        self.token_repository = token_repository
        self.passenger_profile_repository = passenger_profile_repository

    def worker(self,
               token: str) -> int:
        user: UserTable
        try:
            user = self.token_repository.get_user(sha512(token.encode()).digest())
        except NotFound:
            raise UserNotFound()
        except Exception:
            raise InternalServerError()
        
        passenger_id: int
        try:
            passenger_id = self.passenger_profile_repository.insert(user).id
        except UniqueViolation:
            raise ProfileAlreadyExist()
        except Exception:
            raise InternalServerError()
        return passenger_id