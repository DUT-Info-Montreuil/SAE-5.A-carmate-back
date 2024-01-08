from api.worker import Worker
from services import PassengerCodeService


class LookForCarpooling(Worker):
    def worker(self,
               passenger_scheduled_carpooling_id: int):
        user_id = self.propose_scheduled_carpooling_repository.get_user_id_from_scheduled_carpooling(passenger_scheduled_carpooling_id)
        carpoolings_to_reserve = self.propose_scheduled_carpooling_repository.get_carpoolings_to_reserve_for(passenger_scheduled_carpooling_id)

        for carpooling_to_reserve in carpoolings_to_reserve:
            passenger_code = PassengerCodeService.next()
            self.booking_carpooling_repository.insert(user_id,
                                                      carpooling_to_reserve.id,
                                                      passenger_code)

