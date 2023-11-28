from datetime import datetime
from hashlib import sha512

from api.worker.auth.exceptions import InternalServerError
from database.exceptions import NotFound
from database.repositories import TokenRepositoryInterface


class CheckToken:
    token_repository: TokenRepositoryInterface

    def __init__(self,
                 token_repository: TokenRepositoryInterface):
        self.token_repository = token_repository

    def worker(self, token: str) -> bool:
        token_expiration: datetime
        try:
            token_expiration = self.token_repository.get_expiration(sha512(token.encode()).hexdigest())
        except NotFound:
            return False
        except Exception as e:
            raise InternalServerError(str(e))

        return not token_expiration < datetime.today()
