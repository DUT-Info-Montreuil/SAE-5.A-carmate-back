from abc import ABC


class ReserveCarpoolingRepositoryInterface(ABC):
    def dummy(self): ...


class ReserveCarpoolingRepository(ReserveCarpoolingRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "reserve_carpooling"

    def dummy(self):
        return None
