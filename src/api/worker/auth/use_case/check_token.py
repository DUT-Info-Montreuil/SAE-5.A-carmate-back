from datetime import datetime
from hashlib import sha512

from api.exceptions import InternalServerError
from api.worker.auth.models import UserInformationDTO
from database.exceptions import NotFound
from database.schemas import UserTable
from database.repositories import (
    TokenRepositoryInterface,
    UserBannedRepositoryInterface,
    UserAdminRepositoryInterface
)


class CheckToken:
    token_repository: TokenRepositoryInterface
    user_banned_repository: UserBannedRepositoryInterface
    user_admin_repository: UserAdminRepositoryInterface

    def __init__(self,
                 token_repository: TokenRepositoryInterface,
                 user_banned_repository: UserBannedRepositoryInterface,
                 user_admin_repository: UserAdminRepositoryInterface) -> None:
        self.token_repository = token_repository
        self.user_banned_repository = user_banned_repository
        self.user_admin_repository = user_admin_repository

    def worker(self, token: str) -> None | UserInformationDTO:
        token_hashed = sha512(token.encode()).digest()

        token_expiration: datetime
        try:
            token_expiration = self.token_repository.get_expiration(token_hashed)
        except NotFound:
            return None
        except Exception as e:
            raise InternalServerError(str(e))
        
        if token_expiration < datetime.today():
            return None
        
        user: UserTable
        try:
            user = self.token_repository.get_user(token_hashed)
        except NotFound:
            return None
        except Exception as e:
            raise InternalServerError(str(e))

        return UserInformationDTO(self.user_admin_repository.is_admin(user.id), self.user_banned_repository.is_banned(user.id))
