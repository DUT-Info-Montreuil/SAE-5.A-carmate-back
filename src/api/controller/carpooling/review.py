from flask import (
    Blueprint,
    request,
    abort
)

from api.controller.carpooling import (
    URL_ROUTE_PREFIX,
    token_is_valid,
    extract_token
)
from api.exceptions import (
    CarpoolingNotFound,
    CarpoolingReviewTimeExpired,
    PassengerNotFound
)
from api.worker.carpooling.models import ReviewDTO
from api.worker.carpooling.use_case import CreateReview
from database.exceptions import UniqueViolation


class ReviewRoutes(Blueprint):
    def __init__(self) -> None:
        super().__init__("review_carpooling", __name__,
                         url_prefix=URL_ROUTE_PREFIX)

        self.before_request(token_is_valid)
        self.route("/review",
                   methods=["POST"])(self.review_carpooling_api)

    def review_carpooling_api(self):
        if not request.is_json:
            abort(415)

        economic_driving_rating: float
        safe_driving_rating: float
        sociability_rating: float
        review: str
        driver_id: int

        data = request.get_json()
        if "economic_driving_rating" not in data \
                or "safe_driving_rating" not in data \
                or "sociability_rating" not in data \
                or "review" not in data \
                or "driver_id" not in data:
            abort(400)

        try:
            economic_driving_rating = float(data["economic_driving_rating"])
            safe_driving_rating = float(data["safe_driving_rating"])
            sociability_rating = float(data["sociability_rating"])
            review = data["review"]
            driver_id = int(data["driver_id"])
        except ValueError:
            abort(400)
        except Exception:
            abort(500)

        if not (0 <= economic_driving_rating <= 5) \
                or not (0 <= safe_driving_rating <= 5) \
                or not (0 <= sociability_rating <= 5) \
                or driver_id < 0 \
                or review is None:
            abort(400)
        review_dto = ReviewDTO(economic_driving_rating,
                               safe_driving_rating,
                               sociability_rating,
                               review,
                               driver_id)
        try:
            CreateReview().worker(review_dto, extract_token())
        except PassengerNotFound:
            abort(403)
        except CarpoolingNotFound:
            abort(404)
        except CarpoolingReviewTimeExpired:
            abort(408)
        except UniqueViolation:
            abort(409)
        except Exception:
            abort(500)
        return '', 204
