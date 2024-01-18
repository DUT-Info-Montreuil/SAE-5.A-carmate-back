from dataclasses import dataclass


@dataclass
class ReviewDTO:
    economic_driving_rating: float
    safe_driving_rating: float
    sociability_rating: float
    review: str
    driver_id: int

    @staticmethod
    def to_self(_tuple: tuple):
        return ReviewDTO(
            _tuple[0],
            _tuple[1],
            _tuple[2],
            _tuple[3],
            _tuple[4],
        )
