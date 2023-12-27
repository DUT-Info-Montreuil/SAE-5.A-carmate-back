from datetime import datetime
from hashlib import sha512

from api.worker import Worker
from api.worker.admin import DocumentType, ValidationStatus
from api.worker.auth.models import UserInformationDTO
from api.exceptions import InternalServerError
from database.schemas import UserTable, LicenseTable
from database.exceptions import NotFound


class CheckToken(Worker):
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

        driver_license: LicenseTable
        driver_license_valid: bool
        try:
            driver_license = self.license_repository.get_license_by_user_id(user.id, DocumentType.Driver.name)
        except NotFound:
            driver_license_valid = False
        except Exception as e:
            raise InternalServerError(str(e))
        else:
            driver_license_valid = driver_license.validation_status == ValidationStatus.Approved.name

        return UserInformationDTO(self.user_admin_repository.is_admin(user.id), self.user_banned_repository.is_banned(user.id), driver_license_valid)
