import copy
import random

from datetime import datetime, timedelta
from typing import List, Tuple

from database.interfaces import CarpoolingRepositoryInterface
from database.schemas import (
    CarpoolingTable,
    ReserveCarpoolingTable,
    Weekday
)
from database.exceptions import CheckViolation, NotFound


class InMemoryCarpoolingRepository(CarpoolingRepositoryInterface):
    RADIUS: float = .07

    def __init__(self, reserve_carpooling_repository=None) -> None:
        self.reserve_carpooling_repository = reserve_carpooling_repository
        self.carpoolings: List[CarpoolingTable] = [
            CarpoolingTable(1, [48.883078, 2.343902], [48.839678, 2.375806], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=1), 1),
            CarpoolingTable(2, [48.857662, 2.294402], [48.844277, 2.280792], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=5), 2),
            CarpoolingTable(3, [48.858435, 2.274930], [48.873241, 2.293537], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=3), 2),
            CarpoolingTable(4, [48.861757, 2.348029], [48.929428, 2.356391], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=6), 1),
            CarpoolingTable(5, [48.855298, 2.344935], [48.853408, 2.369272], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=31), 2),
            CarpoolingTable(6, [48.855277, 2.346775], [48.847707, 2.358453], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=12), 1),
            CarpoolingTable(7, [48.865482, 2.417373], [48.864703, 2.320528], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=3), 1),
            CarpoolingTable(8, [48.876021, 2.338564], [48.853602, 2.333788], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=4), 1),
            CarpoolingTable(9, [48.820259, 2.339703], [48.821747, 2.368704], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=80), 2),
            CarpoolingTable(10, [48.836789, 2.373223], [48.841768, 2.389111], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=14), 1),
            CarpoolingTable(11, [48.847213, 2.395915], [48.866928, 2.363830], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=6), 1),
            CarpoolingTable(12, [48.882998, 2.370094], [48.895817, 2.393677], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=8), 2),
            CarpoolingTable(13, [48.843487, 2.374254], [48.979739, 2.553426], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=14), 1),
            CarpoolingTable(14, [48.727642, 2.369743], [48.853190, 2.350634], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=55), 2),
            CarpoolingTable(15, [48.740541, 2.361311], [48.857840, 2.295190], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=24), 2),
            CarpoolingTable(16, [48.732060, 2.370990], [48.859222, 2.293382], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=31), 1),
            CarpoolingTable(17, [48.731592, 2.372117], [48.857649, 2.300376], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=30), 1),
            CarpoolingTable(18, [48.861426, 2.349818], [48.862138, 2.462982], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=7), 2),
            CarpoolingTable(19, [48.859498, 2.347059], [48.863081, 2.463577], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=5), 2),
            CarpoolingTable(20, [48.857363, 2.352354], [48.861962, 2.466196], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=57), 2),
            CarpoolingTable(21, [48.876999, 2.357839], [48.860242, 2.466126], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=6), 2),
            CarpoolingTable(22, [48.880775, 2.360230], [48.862154, 2.461164], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=1), 1),
            CarpoolingTable(23, [48.843350, 2.374057], [48.975527, 2.561268], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=45), 1),
            CarpoolingTable(24, [48.853686, 2.369441], [48.976223, 2.561324], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=8), 1),
            CarpoolingTable(25, [48.843492, 2.373834], [48.975508, 2.559423], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=1), 2),
            CarpoolingTable(26, [48.877086, 2.361286], [48.966698, 2.562614], 4, round(random.uniform(1, 50), 2), False, datetime.now() + timedelta(days=1), 2),
            CarpoolingTable(27, [48.877890, 2.361387], [48.968698, 2.552614], 4, round(random.uniform(1, 50), 2), True, datetime.now() + timedelta(days=30), 2),
            CarpoolingTable(28, [48.727642, 2.349818], [48.841768, 2.350634], 4, round(random.uniform(1, 50), 2), False, datetime.now() - timedelta(days=30), 2)
        ]
        self.licenses_count = len(self.carpoolings)

    def get_carpoolings_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        departure_date_time: int,
        page: int = 1,
        per_page: int = 10
    ) -> Tuple[int, List[CarpoolingTable]]:
        if self.reserve_carpooling_repository is None:
            raise Exception("To use the fucntion get_carpoolings_route you need the reserve carpooling repository")

        filtered_carpoolings = copy.deepcopy([
            carpooling for carpooling in self.carpoolings
            if (
                abs(carpooling.starting_point[0] - start_lat) < self.RADIUS
                and abs(carpooling.starting_point[1] - start_lon) < self.RADIUS
                and abs(carpooling.destination[0] - end_lat) < self.RADIUS
                and abs(carpooling.destination[1] - end_lon) < self.RADIUS
                and carpooling.departure_date_time >= datetime.utcfromtimestamp(departure_date_time)
            )
        ])

        for carpooling in filtered_carpoolings:
            carpooling.seats_taken = 0
            for reserved_carpoolings in self.reserve_carpooling_repository.reserved_carpoolings:
                if reserved_carpoolings.carpooling_id == carpooling.id:
                    carpooling.seats_taken += 1

        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        return len(filtered_carpoolings), filtered_carpoolings[start_index:end_index]

    def insert(self,
               driver_id: int,
               starting_point: List[float],
               destination: List[float],
               max_passengers: int,
               price: float,
               departure_date_time: int) -> int:

        if not (41.3 <= starting_point[0] <= 51.1 and -5.142 <= starting_point[1] <= 9.561):
            raise CheckViolation("Starting_point invalid")

        if not (41.3 <= destination[0] <= 51.1 and -5.142 <= destination[1] <= 9.561):
            raise CheckViolation("Destination invalid")

        carpooling = CarpoolingTable(self.licenses_count,
                                     starting_point,
                                     destination,
                                     max_passengers,
                                     price,
                                     False,
                                     datetime.fromtimestamp(departure_date_time),
                                     driver_id)
        self.carpoolings.append(carpooling)
        self.licenses_count += 1
        return carpooling.id

    def get_from_id(self, 
                    carpooling_id: int) -> CarpoolingTable:
        for carpooling in self.carpoolings:
            if carpooling.id == carpooling_id:
                return carpooling
        raise NotFound("carpooling not found")

    def get_last_carpooling_between(self, driver_id: int, user_id: int) -> CarpoolingTable:
        if self.reserve_carpooling_repository is None:
            raise Exception("To use the fucntion get_carpoolings_route you need the reserve carpooling repository")

        carpooling_list: List[CarpoolingTable] = []
        for carpooling in self.carpoolings:
            if carpooling.driver_id == driver_id and carpooling.is_canceled is False:
                carpooling_list.append(carpooling)

        if len(carpooling_list) == 0:
            raise NotFound("There are no carpooling existing between these two users")

        filtered_carpooling_list: List[CarpoolingTable] = []
        for carpooling in carpooling_list:
            for reserve_carpooling in self.reserve_carpooling_repository.reserved_carpoolings:
                if reserve_carpooling.user_id == user_id \
                        and reserve_carpooling.carpooling_id == carpooling.id \
                        and reserve_carpooling.passenger_code_validated \
                        and not reserve_carpooling.canceled:
                    filtered_carpooling_list.append(carpooling)

        if len(filtered_carpooling_list) == 0:
            raise NotFound("There are no carpooling existing between these two users")
        return sorted(filtered_carpooling_list, key=lambda x: x.departure_date_time, reverse=True)[0]

    def has_carpooling_between_dates_at_hour(self,
                                             start_date: datetime.date,
                                             end_date: datetime.date,
                                             at_time: datetime.time,
                                             on_days: List[Weekday],
                                             driver_id: int) -> bool:
        return any(
            carpooling for carpooling in self.carpoolings
            if not carpooling.is_canceled
            and start_date <= carpooling.departure_date_time.date() <= end_date
            and carpooling.departure_date_time.time() == at_time
            and Weekday(carpooling.departure_date_time.weekday() + 1) in on_days
        )

    def has_carpooling_at(self,
                          driver_id: int,
                          timestamp: int) -> bool:
        for carpooling in self.carpoolings:
            if carpooling.driver_id == driver_id \
                    and carpooling.departure_date_time.timestamp() == timestamp \
                    and not carpooling.is_canceled:
                return True
        return False
