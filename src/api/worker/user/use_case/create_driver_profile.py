from hashlib import sha512
from typing import IO

from api.worker import Worker
from api.worker.admin import DocumentType
from api.worker.user.models import DriverProfileDTO
from api.exceptions import (
    UserNotFound,
    InternalServerError,
    ProfileAlreadyExist
)
from database.schemas import DriverProfileTable, UserTable
from database.exceptions import (
    NotFound,
    UniqueViolation
)


class CreateDriverProfile(Worker):
    def worker(self,
               token: str,
               document: IO[bytes]) -> DriverProfileDTO:
        user: UserTable
        try:
            user = self.token_repository.get_user(sha512(token.encode()).digest())
        except NotFound:
            raise UserNotFound()
        except Exception as e:
            raise InternalServerError(str(e))

        driver: DriverProfileTable
        try:
            driver = self.driver_profile_repository.insert(user)
        except UniqueViolation:
            raise ProfileAlreadyExist()
        except Exception as e:
            raise InternalServerError(str(e))
    
        try:
            self.license_repository.insert(document.read(), user, DocumentType.Driver.name)
        except Exception as e:
            raise InternalServerError(str(e))
        return DriverProfileDTO.from_table(driver)
