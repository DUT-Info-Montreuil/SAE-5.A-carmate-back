from hashlib import sha512
from typing import IO

from api.exceptions import (
    UserNotFound,
    InternalServerError,
    ProfileAlreadyExist
)
from api.worker.admin import DocumentType
from database.schemas import UserTable
from database.exceptions import (
    NotFound,
    UniqueViolation
) 
from database.repositories import (
    TokenRepositoryInterface, 
    DriverProfileRepositoryInterface,
    LicenseRepositoryInterface
)


class CreateDriverProfile:
    token_repository: TokenRepositoryInterface
    driver_profile_repository: DriverProfileRepositoryInterface
    license_repository: LicenseRepositoryInterface

    def __init__(self,
                 token_repository: TokenRepositoryInterface,
                 driver_profile_repository: DriverProfileRepositoryInterface,
                 license_repository) -> None:
        self.token_repository = token_repository
        self.driver_profile_repository = driver_profile_repository
        self.license_repository = license_repository

    def worker(self,
               token: str,
               document: IO[bytes]) -> int:
        user: UserTable
        try:
            user = self.token_repository.get_user(sha512(token.encode()).digest())
        except NotFound:
            raise UserNotFound()
        except Exception as e:
            raise InternalServerError(str(e))

        driver_id: int
        try:
            driver_id = self.driver_profile_repository.insert(user).id
        except UniqueViolation:
            raise ProfileAlreadyExist()
        except Exception as e:
            raise InternalServerError(str(e))
    
        try:
            self.license_repository.insert(document.read(), user, DocumentType.Driver.name)
        except Exception as e:
            raise InternalServerError(str(e))
        return driver_id
