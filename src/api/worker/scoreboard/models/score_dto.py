from dataclasses import dataclass, asdict
from typing import Optional


@dataclass(frozen=True)
class ScoreDTO:
    driver_id: int
    first_name: str
    last_name: str
    profile_picture: bytes
    nb_review: int
    nb_carpooling_done: int
    economic_driving_rating: Optional[float] = None
    safe_driving_rating: Optional[float] = None
    sociability_rating: Optional[float] = None

    def to_json(self) -> dict:
        json_from_dto = asdict(self)
        if self.economic_driving_rating is None:
            json_from_dto.pop("economic_driving_rating")
        elif self.safe_driving_rating is None:
            json_from_dto.pop("safe_driving_rating")
        elif self.sociability_rating is None:
            json_from_dto.pop("sociability_rating")
        return json_from_dto
