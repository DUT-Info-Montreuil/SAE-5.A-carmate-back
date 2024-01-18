from hashlib import sha512

from api.worker import Worker
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


class CreatePassengerProfile(Worker):
    def worker(self,
               token: str) -> int:
        user: UserTable
        try:
            user = self.token_repository.get_user(sha512(token.encode()).digest())
        except NotFound:
            raise UserNotFound()
        except Exception as e:
            raise InternalServerError(str(e))
        
        passenger_id: int
        try:
            passenger_id = self.passenger_profile_repository.insert(user).id
        except UniqueViolation:
            raise ProfileAlreadyExist()
        except Exception as e:
            raise InternalServerError(str(e))
        return passenger_id