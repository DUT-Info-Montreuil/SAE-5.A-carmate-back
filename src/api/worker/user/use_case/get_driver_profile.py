from hashlib import sha512
from typing import Tuple

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
        average_criterions: Tuple[int, float, float, float] | None = None
        if token is not None:
            try:
                user = self.token_repository.get_user(sha512(token.encode()).digest())
                driver_profile, picture_profile = self.driver_profile_repository.get_driver_by_user_id(user.id)
                average_criterions = self.driver_profile_repository.get_average_criterions_from_driver(user.id)
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
        
        if average_criterions is None:
            return DriverProfileDTO.from_table(driver_profile).set_profile_picture(picture_profile)

        elif average_criterions[1] == 0:
            return DriverProfileDTO.from_table(driver_profile).set_profile_picture(picture_profile)
        
        return DriverProfileDTO\
            .from_table(driver_profile)\
            .average_economic_driving_ratings(average_criterions[0])\
            .average_safe_driving_ratings(average_criterions[1])\
            .average_sociability_ratings(average_criterions[2])\
            .set_profile_picture(picture_profile)
