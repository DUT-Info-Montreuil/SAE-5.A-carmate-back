from datetime import datetime

from api.worker import Worker
from services import PassengerCodeService


class LookForPassengers(Worker):
    def worker(self,
               passenger_carpooling_id: int):
        scheduled_carpooling = self.scheduled_carpooling_repository.get_scheduled_carpooling(passenger_carpooling_id)
        reservations_to_do = self.scheduled_carpooling_repository.get_passengers_for_schedule_carpooling(
            passenger_carpooling_id)

        reservations = dict()
        for reservation in reservations_to_do:
            reservations.setdefault(reservation[1], []).append(reservation[0])

        for date, user_ids in reservations.items():
            carpooling_id = self.carpooling_repository.insert(scheduled_carpooling.driver_id,
                                                              scheduled_carpooling.starting_point,
                                                              scheduled_carpooling.destination,
                                                              scheduled_carpooling.max_passengers,
                                                              0,
                                                              int(date.timestamp()))
            for user_id in user_ids:
                self.booking_carpooling_repository.insert(user_id,
                                                          carpooling_id,
                                                          PassengerCodeService.next())


