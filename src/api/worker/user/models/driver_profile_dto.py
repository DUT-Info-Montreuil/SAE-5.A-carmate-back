from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Tuple

from database.schemas import DriverProfileTable


@dataclass
class DriverProfileDTO:
    id: int
    description: str
    created_at: datetime
    user_id: int
    average_economic_driving_ratings: Optional[float] | None = None
    average_safe_driving_ratings: Optional[float] | None = None
    average_sociability_ratings: Optional[float] | None = None
    profile_picture: Optional[bytes] | None = None
    
    @staticmethod
    def from_table(table: DriverProfileTable) -> DriverProfileDTO:
        return DriverProfileDTO(
            table.id,
            table.description,
            table.created_at,
            table.user_id
        )
    

    def set_profile_picture(self,
                            new_profile_picture: bytes | None) -> DriverProfileDTO:
        self.profile_picture = new_profile_picture
        return self

    def average_economic_driving_ratings(self,
                                          new_average_economic_driving_ratings: float | None) -> DriverProfileDTO:
        self.average_economic_driving_ratings = new_average_economic_driving_ratings
        return self

    def average_safe_driving_ratings(self,
                                      new_average_safe_driving_ratings: float | None) -> DriverProfileDTO:
        self.average_safe_driving_ratings = new_average_safe_driving_ratings
        return self

    def average_sociability_ratings(self,
                                     new_average_sociability_ratings: float | None) -> DriverProfileDTO:
        self.average_sociability_ratings = new_average_sociability_ratings
        return self
    
    def to_json(self):
        return asdict(self)
