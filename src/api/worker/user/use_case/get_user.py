from hashlib import sha512

from api.worker import Worker
from api.worker.user.models import UserDTO
from api.exceptions import InternalServerError, UserNotFound
from database.schemas import UserTable
from database.exceptions import NotFound


class GetUser(Worker):
    def worker(self,
               user_id: int | None = None,
               token: str | None = None) -> UserDTO:
        user: UserTable | None = None
        if token is not None:
            try:
                user = self.token_repository.get_user(sha512(token.encode()).digest())
            except NotFound:
                raise UserNotFound()
            except Exception as e:
                raise InternalServerError(str(e))
        elif user_id is not None:
            try:
                user = self.user_repository.get_user_by_id(user_id)
            except NotFound:
                raise UserNotFound()
            except Exception as e:
                raise InternalServerError(str(e))
        else:
            raise UserNotFound()
        return UserDTO(user.first_name, user.last_name, user.email_address, user.created_at, user.profile_picture)
