from api.exceptions import InternalServerError, InvalidValidationStatus, LicenseNotFound
from database.exceptions import InvalidInputEnumValue, NotFound
from database.repositories import LicenseRepositoryInterface, UserRepositoryInterface
from database.schemas import LicenseTable, UserTable


class ValidateLicense:
    license_repository: LicenseRepositoryInterface

    def __init__(self, 
                 license_repository: LicenseRepositoryInterface,
                 user_repository: UserRepositoryInterface):
        self.license_repository = license_repository
        self.user_repository = user_repository

    def worker(self, license_id: int, validate_status: str):
        try:
            self.license_repository.update_status(license_id, validate_status)
        except NotFound as e:
            raise LicenseNotFound(str(e))
        except InvalidInputEnumValue as e:
            raise InvalidValidationStatus(str(e))
        except Exception as e:
            raise InternalServerError(str(e))
        
        license_table: LicenseTable
        try:
            license_table = self.license_repository.get(license_id + 1)
        except NotFound:
            return None
        except Exception as e:
            raise InternalServerError(str(e))

        user_table: UserTable
        try:
            user_table = self.user_repository.get_user_by_id(license_table.user_id)
        except NotFound:
            return None
        except Exception as e:
            raise InternalServerError(str(e))
        
        return (license_table, user_table)
