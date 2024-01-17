from hashlib import sha512
from typing import List, Tuple

from api.worker import Worker
from api.exceptions import InternalServerError
from api.worker.user.models import ProposeScheduledCarpoolingDTO
from database.schemas import CarpoolingTable, UserTable


class GetProposeScheduledCarpoolings(Worker):
    def worker(self,
               token: str) -> List[ProposeScheduledCarpoolingDTO]:
        user: UserTable
        try:
            user = self.token_repository.get_user(sha512(token.encode()).digest())
        except Exception as e:
            raise InternalServerError(str(e))
        
        propose_scheduled_carpoolings: List[Tuple[CarpoolingTable, int, str, str]]
        try:
            propose_scheduled_carpoolings = self.propose_scheduled_carpooling_repository.get_propose_scheduled_carpoolings_from_user_id(user.id)
        except Exception as e:
            raise InternalServerError(str(e))
        return [ProposeScheduledCarpoolingDTO(*propose_scheduled_carpooling) for propose_scheduled_carpooling in propose_scheduled_carpoolings]
        