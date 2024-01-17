from hashlib import sha512
from typing import List

from api.worker import Worker
from api.exceptions import InternalServerError
from api.worker.user.models import PublishedScheduleCarpoolingDTO
from database.schemas import DriverProfileTable, DriverScheduledCarpoolingTable


class GetPublishedScheduleCarpooling(Worker):
    def worker(self,
               token: str) -> List[PublishedScheduleCarpoolingDTO]:
        driver_profile: DriverProfileTable
        try:
            driver_profile = self.token_repository.get_driver_profile(sha512(token.encode()).digest())
        except Exception as e:
            raise InternalServerError(str(e))
        
        scheduled_carpoolings: List[DriverScheduledCarpoolingTable]
        try:
            scheduled_carpoolings = self.scheduled_carpooling_repository.get_scheduled_carpooling_created_by(driver_profile.id)
        except Exception as e:
            raise InternalServerError(str(e))
        return [PublishedScheduleCarpoolingDTO(*scheduled_carpooling) for scheduled_carpooling in scheduled_carpoolings]

