from hashlib import sha512

from api.worker.user.models import PassengerProfileDTO, DriverProfileDTO
from api.exceptions import (
    DriverNotFound,
    InternalServerError
)
from database.exceptions import NotFound
from database.schemas import DriverProfileTable
from database.repositories import (
    TokenRepositoryInterface, 
    DriverProfileRepositoryInterface
)


class GetDriverProfile:
    token_repository: TokenRepositoryInterface
    driver_profile_repository: DriverProfileRepositoryInterface

    def __init__(self,
                 token_repository: TokenRepositoryInterface,
                 driver_profile_repository: DriverProfileRepositoryInterface) -> None:
        self.token_repository = token_repository
        self.driver_profile_repository = driver_profile_repository

    def worker(self,
               driver_id: int=None,
               token: str=None) -> DriverProfileDTO:
        driver_profile: DriverProfileTable = None
        if token is not None:
            try:
                user = self.token_repository.get_user(sha512(token.encode()).digest())
                driver_profile = self.driver_profile_repository.get_driver_by_user_id(user.id)
            except NotFound:
                raise DriverNotFound()
            except Exception as e:
                raise InternalServerError(str(e))
        elif driver_id is not None:
            try:
                driver_profile = self.driver_profile_repository.get_driver(driver_id)
            except NotFound:
                raise DriverNotFound()
            except Exception as e:
                raise InternalServerError(str(e))
        else:
            raise DriverNotFound()
        return DriverProfileDTO(driver_profile.description, driver_profile.created_at)
