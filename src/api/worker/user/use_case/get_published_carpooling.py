from hashlib import sha512
from typing import List

from api.worker import Worker
from api.worker.user.models import PublishedCarpoolingDTO


class GetPublishedCarpooling(Worker):
    def worker(self,
               driver_id: int) -> List[PublishedCarpoolingDTO]:
        carpoolings = self.carpooling_repository.get_carpooling_created_by(driver_id)
        
        published_carpoolings: List[PublishedCarpoolingDTO] = []
        for carpooling in carpoolings:
            passengers_from_carpooling = self.booking_carpooling_repository.get_passengers_from_carpooling(carpooling.id)
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
