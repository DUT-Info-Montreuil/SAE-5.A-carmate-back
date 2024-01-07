from hashlib import sha512

from api.worker import Worker
from api.worker.user.models import DriverProfileDTO
from api.exceptions import (
    DriverNotFound,
    InternalServerError
)
from database.schemas import DriverProfileTable
from database.exceptions import NotFound


class GetDriverProfile(Worker):
    def worker(self,
               driver_id: int=None,
               token: str=None) -> DriverProfileDTO:
        driver_profile: DriverProfileTable
        picture_profile: bytes | None
        if token is not None:
            try:
                user = self.token_repository.get_user(sha512(token.encode()).digest())
                driver_profile, picture_profile = self.driver_profile_repository.get_driver_by_user_id(user.id)
            except NotFound:
                raise DriverNotFound()
            except Exception as e:
                raise InternalServerError(str(e))
        elif driver_id is not None:
            try:
                driver_profile, picture_profile = self.driver_profile_repository.get_driver(driver_id)
            except NotFound:
                raise DriverNotFound()
            except Exception as e:
                raise InternalServerError(str(e))
        else:
            raise DriverNotFound()
        return DriverProfileDTO.from_table(driver_profile).set_profile_picture(picture_profile)
