from typing import List

from api.worker import Worker
from api.worker.user.models import UserDTO
from api.worker.user.use_case import GetUser
from api.exceptions import UserNotFound, InternalServerError
from database.schemas import ReserveCarpoolingTable


class GetHistory(Worker):
    def worker(self,
               token: str):
        user: UserDTO
        try:
            user = GetUser().worker(token=token)
        except UserNotFound as e:
            raise e
        except Exception as e:
            raise e
        
        carpoolings_done: List[ReserveCarpoolingTable]
        try:
            carpoolings_done = self.booking_carpooling_repository.done_from_user_id(user.id)
        except Exception as e:
            raise InternalServerError(e)
        return carpoolings_done
