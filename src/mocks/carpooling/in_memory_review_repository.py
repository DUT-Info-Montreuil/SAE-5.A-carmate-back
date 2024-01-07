from datetime import datetime
from typing import List

from database.interfaces import ReviewRepositoryInterface
from database.schemas import ReviewTable
from database.exceptions import UniqueViolation


class InMemoryReviewRepository(ReviewRepositoryInterface):
    def __init__(self):
        self.reviews: List[ReviewTable] = []

    def insert(self, review, user_id: int):
        for self_review in self.reviews:
            if self_review.driver_id == review.driver_id \
                    and self_review.user_id == user_id:
                raise UniqueViolation("The review already exists")

        self.reviews.append(ReviewTable(
            user_id,
            review.driver_id,
            review.economic_driving_rating,
            review.safe_driving_rating,
            review.sociability_rating,
            review.review,
            datetime.now(),
            datetime.now()
        ))
