from hashlib import sha512
from typing import List

from database.repositories import CarpoolingRepositoryInterface, TokenRepositoryInterface
from datetime import datetime


class CreateCarpooling:
    carpooling_repository: CarpoolingRepositoryInterface
    token_repository: TokenRepositoryInterface

    def __init__(self,
                 carpooling_repository: CarpoolingRepositoryInterface,
                 token_repository: TokenRepositoryInterface) -> None:
        self.carpooling_repository = carpooling_repository
        self.token_repository = token_repository

    def worker(self,
               token: str,
               starting_point: List[float],
               destination: List[float],
               max_passengers: int,
               price: float,
               departure_date_time: int) -> int:
        driver = self.token_repository.get_driver_profile(sha512(token.encode()).digest())

        return self.carpooling_repository.insert(driver.id, starting_point, destination, max_passengers, price, departure_date_time)
