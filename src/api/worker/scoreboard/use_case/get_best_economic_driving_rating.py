from typing import List, Tuple

from api.worker import Worker
from api.worker.scoreboard.models import ScoreDTO
from api.exceptions import InternalServerError
from database.schemas import UserTable


class GetBestEconomicDrivingRating(Worker):
    def worker(self) -> List[ScoreDTO]:
        list_best_drivers: List[Tuple[UserTable, int, float, int, int]]
        try:
            list_best_drivers = self.review_repository.get_list_best_drivers_according_economic_driving_rating_criterion()
        except Exception as e:
            raise InternalServerError(str(e))
        return [ScoreDTO(driver_id,
                         user.first_name,
                         user.last_name,
                         user.profile_picture,
                         nb_review,
                         nb_carpooling_done,
                         economic_driving_rating=economic_driving_rating)
                for user, driver_id, economic_driving_rating, nb_review, nb_carpooling_done in list_best_drivers]
