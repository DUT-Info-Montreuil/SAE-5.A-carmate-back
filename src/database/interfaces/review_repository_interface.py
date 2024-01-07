from abc import ABC

from api.worker.carpooling.models import ReviewDTO


class ReviewRepositoryInterface(ABC):
    def insert(self,
               review: ReviewDTO,
               passenger_id: int): ...
