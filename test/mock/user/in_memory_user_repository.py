from typing import List

from api.worker.auth.models import CredentialDTO
from database.exceptions import UniqueViolation
from database.repositories import UserRepositoryInterface
from database.schemas import UserTable


class InMemoryUserRepository(UserRepositoryInterface):
    users: List[UserTable] = []
    users_counter: int = 0

    @staticmethod
    def insert(credential: CredentialDTO) -> UserTable:
        first_name, last_name, email_address, password = credential.to_json().values()

        for user in InMemoryUserRepository.users:
            if user.email_address == email_address:
                raise UniqueViolation()

        in_memory_user = UserTable.to_self((InMemoryUserRepository.users_counter,
                                            first_name,
                                            last_name,
                                            email_address,
                                            password,
                                            None))
        InMemoryUserRepository.users.append(in_memory_user)
        InMemoryUserRepository.users_counter = InMemoryUserRepository.users_counter + 1
        return in_memory_user
