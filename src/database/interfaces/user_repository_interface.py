from abc import ABC

from api.worker.auth.models import CredentialDTO
from api.worker.user import AccountStatus
from database.schemas import UserTable


class UserRepositoryInterface(ABC):
    def insert(self,
               credential: CredentialDTO,
               account_status: AccountStatus) -> UserTable: ...

    def get_user_by_email(self,
                          email: str) -> UserTable: ...

    def get_user_by_id(self,
                       id: int) -> UserTable: ...
