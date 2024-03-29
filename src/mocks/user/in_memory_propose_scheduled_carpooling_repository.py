from datetime import timedelta, datetime
from typing import List

from database.exceptions import UniqueViolation, NotFound
from database.interfaces import ProposeScheduledCarpoolingRepositoryInterface
from database.schemas import (
    PassengerScheduledCarpoolingTable,
    PassengerProfileTable,
    CarpoolingTable,
    Weekday,
    DriverScheduledCarpoolingTable
)


class InMemoryProposeScheduledCarpoolingRepository(ProposeScheduledCarpoolingRepositoryInterface):
    def __init__(self,
                 booked_carpooling_repository,
                 carpooling_repository,
                 passengers_repository,
                 scheduled_carpooling_repository):
        self.propose_scheduled_carpooling_count = 0
        self.propose_scheduled_carpoolings: List[PassengerScheduledCarpoolingTable] = []
        self.booked_carpooling_repository = booked_carpooling_repository
        self.carpooling_repository = carpooling_repository
        self.passengers_repository = passengers_repository
        self.scheduled_carpooling_repository = scheduled_carpooling_repository

    def insert(self,
               label: str,
               starting_point: List[float],
               destination: List[float],
               start_date: datetime.date,
               end_date: datetime.date,
               start_hour: datetime.time,
               days: List[Weekday],
               passenger_id: int) -> int:
        self.propose_scheduled_carpoolings.append(
            PassengerScheduledCarpoolingTable(self.propose_scheduled_carpooling_count,
                                              label,
                                              starting_point,
                                              destination,
                                              start_date,
                                              end_date,
                                              start_hour,
                                              days,
                                              passenger_id))
        self.propose_scheduled_carpooling_count += 1

        return self.propose_scheduled_carpooling_count - 1

    def has_same_time_proposed_scheduled_carpooling(self,
                                                    start_date: datetime.date,
                                                    end_date: datetime.date,
                                                    days: List[Weekday],
                                                    start_hour: datetime.time,
                                                    passenger_id: int) -> bool:
        for propose_scheduled in self.propose_scheduled_carpoolings:
            if start_date <= propose_scheduled.end_date \
                    and propose_scheduled.start_date <= end_date \
                    and bool(set(propose_scheduled.days).intersection(set(days))) \
                    and propose_scheduled.start_hour == start_hour \
                    and propose_scheduled.passenger_id == passenger_id:
                return True
        return False

    def get_user_id_from_scheduled_carpooling(self, propose_scheduled_carpooling_id: int) -> int:
        if not self.booked_carpooling_repository or not self.carpooling_repository or not self.passengers_repository:
            raise Exception(
                "This function won't work without reserve carpooling repository and carpooling repository and passenger profile repository")

        found_scheduled: PassengerScheduledCarpoolingTable = None
        for propose_scheduled in self.propose_scheduled_carpoolings:
            if propose_scheduled.id == propose_scheduled_carpooling_id:
                found_scheduled = propose_scheduled

        if not found_scheduled:
            raise NotFound("User not found for scheduled carpooling")

        found_passenger: PassengerProfileTable
        for passenger in self.passengers_repository.passenger_profiles:
            if passenger.id == found_scheduled.passenger_id:
                found_passenger = passenger

        if not found_passenger:
            raise NotFound("User not found for scheduled carpooling")

        return found_passenger.user_id

    def get_carpoolings_to_reserve_for(self, propose_scheduled_carpooling_id: int) -> List[CarpoolingTable]:
        if not self.booked_carpooling_repository or not self.carpooling_repository or not self.passengers_repository:
            raise Exception(
                "This function won't work without reserve carpooling repository and carpooling repository and passenger profile repository")

        found_scheduled: PassengerScheduledCarpoolingTable = None
        for propose_scheduled in self.propose_scheduled_carpoolings:
            if propose_scheduled.id == propose_scheduled_carpooling_id:
                found_scheduled = propose_scheduled

        if not found_scheduled:
            return []

        found_passenger: PassengerProfileTable = None
        for passenger in self.passengers_repository.passenger_profiles:
            if passenger.id == found_scheduled.passenger_id:
                found_passenger = passenger

        if not found_passenger:
            raise Exception("this should not happen, your datas are wrong")

        reservation_dates = self.get_dates_between(found_scheduled.start_date,
                                                   found_scheduled.end_date,
                                                   found_scheduled.days)

        for booked_carpooling in self.booked_carpooling_repository.reserved_carpoolings:
            if booked_carpooling.user_id == found_passenger.user_id:
                carpooling = self.carpooling_repository.get_from_id(booked_carpooling.carpooling_id)
                if not carpooling.is_canceled \
                        and carpooling.departure_date_time.date() in reservation_dates:
                    reservation_dates.remove(carpooling.departure_date_time.date())

        carpoolings_to_reserve: List[CarpoolingTable] = []

        for carpooling in self.carpooling_repository.carpoolings:
            if not carpooling.is_canceled \
                    and carpooling.starting_point == found_scheduled.starting_point \
                    and carpooling.destination == found_scheduled.destination \
                    and carpooling.departure_date_time.date() in reservation_dates \
                    and carpooling.departure_date_time.time() == found_scheduled.start_hour:
                carpoolings_to_reserve.append(carpooling)

        filtered_carpoolings: List[CarpoolingTable] = carpoolings_to_reserve
        for carpooling in carpoolings_to_reserve:
            number_of_reservations = 0
            for reservation in self.booked_carpooling_repository.reserved_carpoolings:
                if reservation.carpooling_id == carpooling.id:
                    number_of_reservations += 1
            if number_of_reservations >= carpooling.max_passengers:
                filtered_carpoolings.remove(carpooling)
                
        unique_departure_times = set()
        unique_carpoolings: List[CarpoolingTable] = []

        for carpooling in filtered_carpoolings:
            if carpooling.departure_date_time not in unique_departure_times:
                unique_departure_times.add(carpooling.departure_date_time)
                unique_carpoolings.append(carpooling)

        return unique_carpoolings

    def get_dates_between(self, start_date, end_date, weekdays):
        current_date = start_date
        all_matching_dates = []
        numbers_week_day = [weekday.value for weekday in weekdays]
        while current_date <= end_date:
            if current_date.weekday() + 1 in numbers_week_day:
                all_matching_dates.append(current_date)

            current_date += timedelta(days=1)

        return all_matching_dates

    def get_matching_proposed_scheduled_carpooling(self,
                                                   starting_point: List[float],
                                                   destination: List[float],
                                                   date: datetime.date,
                                                   time: datetime.time,
                                                   limit: int) -> List[int]:
        result: List[int] = []
        candidates: List[PassengerScheduledCarpoolingTable] = []
        for proposed_carpool in self.propose_scheduled_carpoolings:
            if proposed_carpool.starting_point == starting_point \
                    and proposed_carpool.destination == destination \
                    and proposed_carpool.start_hour == time \
                    and proposed_carpool.start_date <= date <= proposed_carpool.end_date:
                candidates.append(proposed_carpool)

        count = 0

        for candidate in candidates:
            found_passenger: PassengerProfileTable
            for passenger in self.passengers_repository.passenger_profiles:
                if passenger.id == candidate.passenger_id:
                    found_passenger = passenger

            reservation_dates = self.get_dates_between(candidate.start_date,
                                                       candidate.end_date,
                                                       candidate.days)

            for booked_carpooling in self.booked_carpooling_repository.reserved_carpoolings:
                if booked_carpooling.user_id == found_passenger.user_id:
                    carpooling = self.carpooling_repository.get_from_id(booked_carpooling.carpooling_id)
                    if not carpooling.is_canceled \
                            and carpooling.departure_date_time.date() in reservation_dates:
                        reservation_dates.remove(carpooling.departure_date_time.date())

            if date in reservation_dates:
                result.append(candidate.id)
                count += 1

            if count == limit:
                break

        return result

    def has_scheduled_with_date_and_day(self,
                                        passenger_id: int,
                                        date: datetime.date,
                                        day: Weekday) -> bool:
        for scheduled in self.propose_scheduled_carpoolings:
            if scheduled.passenger_id == passenger_id \
                    and scheduled.start_date <= date <= scheduled.end_date \
                    and day in scheduled.days:
                return True
        return False

    def get_carpoolings_to_create_and_reserve_for(self,
                                                  propose_scheduled_carpooling_id: int) -> List[tuple[int, datetime, int, List[float], List[float]]]:
        found_scheduled: PassengerScheduledCarpoolingTable
        for propose_scheduled in self.propose_scheduled_carpoolings:
            if propose_scheduled.id == propose_scheduled_carpooling_id:
                found_scheduled = propose_scheduled

        if not found_scheduled:
            return []

        possible_carpoolings: List[DriverScheduledCarpoolingTable] = []
        for scheduled_carpooling in self.scheduled_carpooling_repository.scheduled_carpoolings:
            if scheduled_carpooling.start_date == found_scheduled.start_date \
                    and scheduled_carpooling.end_date == found_scheduled.end_date \
                    and scheduled_carpooling.start_hour == found_scheduled.start_hour \
                    and any(day in scheduled_carpooling.days for day in found_scheduled.days):
                possible_carpoolings.append(scheduled_carpooling)

        response: List[tuple[int, datetime, int, List[float], List[float]]] = []
        for possible_carpooling in possible_carpoolings:
            dates = self.get_dates_between(possible_carpooling.start_date,
                                           possible_carpooling.end_date,
                                           possible_carpooling.days)
            for date in dates:
                if found_scheduled.start_date <= date <= found_scheduled.end_date \
                        and date.weekday() + 1 in [day.value for day in found_scheduled.days]:
                    response.append((possible_carpooling.driver_id,
                                     datetime.combine(date, possible_carpooling.start_hour),
                                     possible_carpooling.max_passengers,
                                     possible_carpooling.starting_point,
                                     possible_carpooling.destination))

        return response
