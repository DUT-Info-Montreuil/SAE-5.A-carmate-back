from typing import List

from database.schemas import ReserveCarpoolingTable
from database.repositories.reserve_carpooling_repository import ReserveCarpoolingRepositoryInterface


class InMemoryReserveCarpoolingRepository(ReserveCarpoolingRepositoryInterface):
    def __init__(self) -> None:
        self.reserved_carpoolings: List[ReserveCarpoolingTable] = []

