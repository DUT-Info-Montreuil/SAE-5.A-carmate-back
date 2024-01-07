from typing import List, Tuple

from api.worker import Worker
from api.worker.scoreboard.models import ScoreDTO
from api.exceptions import InternalServerError
from database.schemas import ReviewTable, UserTable


class GetBestSociabilityRating(Worker):
    def worker(self) -> List[ScoreDTO]:
        list_best_drivers: List[Tuple[UserTable, int, float]]
        try:
            list_best_drivers = self.review_repository.get_list_best_drivers_according_sociability_rating_criterion()
        except Exception as e:
            raise InternalServerError(str(e))
        return [ScoreDTO(driver_id, 
                         user.first_name, 
                         user.last_name, 
                         user.profile_picture, 
                         sociability_rating=sociability_rating) 
                         for user, driver_id, sociability_rating in list_best_drivers]
