from hashlib import sha512
from typing import List

from api.worker import Worker


class CreateCarpooling(Worker):
    def worker(self,
               token: str,
               starting_point: List[float],
               destination: List[float],
               max_passengers: int,
               price: float,
               departure_date_time: int) -> int:
        driver = self.token_repository.get_driver_profile(sha512(token.encode()).digest())

        return self.carpooling_repository.insert(driver.id, starting_point, destination, max_passengers, price, departure_date_time)
