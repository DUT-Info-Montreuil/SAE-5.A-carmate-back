from hashlib import sha512
from typing import List

from api.worker.auth.models import CredentialDTO
from database.exceptions import NotFound, UniqueViolation
from database.repositories import UserRepositoryInterface
from database.schemas import UserTable


class InMemoryUserRepository(UserRepositoryInterface):
    users: List[UserTable] = [
        UserTable.to_self((1, "John", "Doe", "user@example.com", sha512("password".encode('utf-8')).hexdigest(), None))]
    users_counter: int = 0

    @staticmethod
    def insert(credential: CredentialDTO) -> UserTable:
        for user in InMemoryUserRepository.users:
            if credential.email_address == user.email_address:
                raise UniqueViolation()

        first_name, last_name, email_address, password = credential.to_json().values()
        in_memory_user = UserTable.to_self((InMemoryUserRepository.users_counter,
                                            first_name,
                                            last_name,
                                            email_address,
                                            password,
                                            None))
        InMemoryUserRepository.users.append(in_memory_user)
        InMemoryUserRepository.users_counter = InMemoryUserRepository.users_counter + 1
        return in_memory_user

    @staticmethod
    def get_user_by_email(email: str) -> UserTable:
        for user in InMemoryUserRepository.users:
            if user.email_address == email:
                return user

        raise NotFound()
