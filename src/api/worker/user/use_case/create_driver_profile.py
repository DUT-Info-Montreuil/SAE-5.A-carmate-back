from hashlib import sha512
from typing import IO

from api.exceptions import (
    UserNotFound,
    InternalServerError,
    ProfileAlreadyExist
)
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
        except Exception:
            raise InternalServerError()

        driver_id: int
        try:
            driver_id = self.driver_profile_repository.insert(user).id
        except UniqueViolation:
            raise ProfileAlreadyExist()
        except Exception:
            raise InternalServerError()
    
        try:
            self.license_repository.insert(document.read(), user, 'Driver')
        except Exception:
            raise InternalServerError()
        return driver_id
