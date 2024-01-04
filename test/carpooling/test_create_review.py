import random
import unittest

from datetime import datetime, timedelta
from hashlib import sha512

from api.worker import AccountStatus
from api.worker.carpooling.models import ReviewDTO
from api.worker.carpooling.use_case import CreateReview
from api.exceptions import (
    UserNotFound,
    CarpoolingNotFound,
    CarpoolingReviewTimeExpired,
    PassengerNotFound
)
from database.schemas import (
    CarpoolingTable,
    ReserveCarpoolingTable,
    UserTable,
    TokenTable,
    ReviewTable,
    PassengerProfileTable
)
from database.exceptions import UniqueViolation


class CreateReviewTestCase(unittest.TestCase):
    def setUp(self):
        self.create_review = CreateReview()
        self.initialize_data()

    def test_fails_if_token_is_invalid(self):
        with self.assertRaises(PassengerNotFound):
            self.create_review.worker(self.valid_review, "invalid_token")

    def test_fails_if_carpooling_does_not_exists(self):
        self.valid_review.driver_id = 9137183193618
        with self.assertRaises(CarpoolingNotFound):
            self.create_review.worker(self.valid_review, "token-admin-valid")

    def test_fails_if_user_dont_have_carpooling_with_driver(self):
        with self.assertRaises(CarpoolingNotFound):
            self.create_review.worker(self.valid_review, "token-no-trip")

    def test_fails_if_more_than_a_week_passed(self):
        with self.assertRaises(CarpoolingReviewTimeExpired):
            self.create_review.worker(self.valid_review, "token-rating-expired")

    def test_fails_if_review_already_exists(self):
        self.create_review.review_repository.reviews.append(
            ReviewTable(1,
                        self.valid_review.driver_id,
                        self.valid_review.economic_driving_rating,
                        self.valid_review.safe_driving_rating,
                        self.valid_review.sociability_rating,
                        self.valid_review.review,
                        datetime.now(),
                        datetime.now())
        )
        with self.assertRaises(UniqueViolation):
            self.create_review.worker(self.valid_review, "token-admin-valid")


    def initialize_data(self):
        self.valid_review = ReviewDTO(3.5, 2.5, 5, "no review", 1)
        self.create_review.carpooling_repository.carpoolings.append(
            CarpoolingTable(9898, [48.727642, 2.349818], [48.841768, 2.350634], 4, round(random.uniform(1, 50), 2), False,
                            datetime.now() - timedelta(days=1), 1)
        )
        self.create_review.booking_carpooling_repository.reserved_carpoolings.append(
            ReserveCarpoolingTable(
                1,
                9898,
                1234,
                passenger_code_validated=True,
                passenger_code_date_validated=datetime.now() - timedelta(days=1),
                canceled=False
            ),
        )
        self.create_review.user_repository.users.append(
            UserTable(9898, "Jane", "Doe", "driver@example.com", sha512("driver_password".encode('utf-8')).digest(),
                      AccountStatus.Teacher.name, None)
        )
        self.create_review.token_repository.tokens.append(
            TokenTable(sha512("token-no-trip".encode()).digest(), datetime.now() + timedelta(days=1), 9898),
        )
        self.create_review.user_repository.users.append(
            UserTable(59999, "Jane", "Doe", "driver@example.com", sha512("driver_password".encode('utf-8')).digest(),
                      AccountStatus.Teacher.name, None)
        )
        self.create_review.token_repository.tokens.append(
            TokenTable(sha512("token-rating-expired".encode()).digest(), datetime.now() + timedelta(days=1), 59999),
        )
        self.create_review.booking_carpooling_repository.reserved_carpoolings.append(
            ReserveCarpoolingTable(
                59999,
                123456,
                1234,
                passenger_code_validated=True,
                passenger_code_date_validated=datetime.now() - timedelta(days=30),
                canceled=False
            )
        )
        self.create_review.carpooling_repository.carpoolings.append(
            CarpoolingTable(123456, [48.727642, 2.349818], [48.841768, 2.350634], 4, round(random.uniform(1, 50), 2), False,
                            datetime.now() - timedelta(days=30), 1)
        )
        self.create_review.passenger_profile_repository.passenger_profiles.append(
            PassengerProfileTable(1,'', datetime.now(), 1)
        )
        self.create_review.passenger_profile_repository.passenger_profiles.append(
            PassengerProfileTable(9898,'', datetime.now(), 9898)
        )
        self.create_review.passenger_profile_repository.passenger_profiles.append(
            PassengerProfileTable(59999,'', datetime.now(), 59999)
        )

