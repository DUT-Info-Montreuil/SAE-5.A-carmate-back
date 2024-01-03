from hashlib import sha512
from typing import List

from api.worker import Worker
from api.worker.user.models import PublishedCarpoolingDTO
from api.exceptions import InternalServerError
from database.schemas import (
    CarpoolingTable,
    DriverProfileTable,
    PassengerProfileTable
)


class GetPublishedCarpooling(Worker):
    def worker(self,
               token: str) -> List[PublishedCarpoolingDTO]:
        driver_profile: DriverProfileTable
        try:
            driver_profile = self.token_repository.get_driver_profile(sha512(token).digest())
        except Exception as e:
            raise InternalServerError(str(e))
        
        carpoolings: List[CarpoolingTable]
        try:
            carpoolings = self.carpooling_repository.get_carpooling_created_by(driver_profile.id)
        except Exception as e:
            raise InternalServerError(str(e))

        published_carpoolings: List[PublishedCarpoolingDTO] = []
        for carpooling in carpoolings:
            passengers_from_carpooling: List[PassengerProfileTable]
            try:
                passengers_from_carpooling = self.booking_carpooling_repository.get_passengers_from_carpooling(carpooling.id)
            except Exception as e:
                raise InternalServerError(str(e))

            published_carpoolings.append(PublishedCarpoolingDTO(
                carpooling.id,
                carpooling.starting_point,
                carpooling.destination,
                carpooling.max_passengers,
                carpooling.price,
                carpooling.is_canceled,
                carpooling.departure_date_time,
                carpooling.driver_id,
                passengers_from_carpooling
            ))
        return published_carpoolings
