from api.worker import Worker
from services import PassengerCodeService


class CheckForMatchingPassengerScheduled(Worker):
    def worker(self,
               carpooling_id: int) -> None:
        carpooling = self.carpooling_repository.get_from_id(carpooling_id)

        scheduled_ids = self.propose_scheduled_carpooling_repository.get_matching_proposed_scheduled_carpooling(carpooling.starting_point,
                                                                                                                carpooling.destination,
                                                                                                                carpooling.departure_date_time.date(),
                                                                                                                carpooling.departure_date_time.time(),
                                                                                                                carpooling.max_passengers)
        for scheduled_id in scheduled_ids:
            self.booking_carpooling_repository.insert(
                self.propose_scheduled_carpooling_repository.get_user_id_from_scheduled_carpooling(scheduled_id),
                carpooling_id, 
                PassengerCodeService.next()
            )

