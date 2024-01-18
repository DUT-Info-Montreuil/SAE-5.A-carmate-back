from typing import List

from database.interfaces import ScheduledCarpoolingRepositoryInterface
from database.schemas import DriverScheduledCarpoolingTable


class InMemoryScheduledCarpoolingRepository(ScheduledCarpoolingRepositoryInterface):
    def __init__(self):
        self.scheduled_carpoolings: List[DriverScheduledCarpoolingTable] = []
