from hashlib import sha512
from typing import List

from api.worker.auth.models import CredentialDTO
from api.worker.user import AccountStatus
from database.exceptions import NotFound, UniqueViolation
from database.repositories import UserRepositoryInterface
from database.schemas import UserTable


class InMemoryUserRepository(UserRepositoryInterface):

    def __init__(self):
        self.users: List[UserTable] = [
            UserTable.to_self(
                (1, "John", "Doe", "user@example.com", sha512("password".encode('utf-8')).digest(), AccountStatus.Student.name, None))]
        self.users_counter: int = 0

    def insert(self, credential: CredentialDTO, account_status: AccountStatus) -> UserTable:
        for user in self.users:
            if credential.email_address == user.email_address:
                raise UniqueViolation("user already exist")

        first_name, last_name, email_address, password = credential.to_json().values()
        in_memory_user = UserTable.to_self((self.users_counter,
                                            first_name,
                                            last_name,
                                            email_address,
                                            password,
                                            account_status.name,
                                            None))
        self.users.append(in_memory_user)
        self.users_counter = self.users_counter + 1
        return in_memory_user

    def get_user_by_email(self, email: str) -> UserTable:
        for user in self.users:
            if user.email_address == email:
                return user

        raise NotFound("user not found")
    
    def get_user_by_id(self, id: int) -> UserTable:
        for user in self.users:
            if user.id == id:
                return user

        raise NotFound("user not found")
