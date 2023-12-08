from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class UserInformationDTO:
    admin: bool
    banned: bool

    def to_json(self) -> dict:
        return asdict(self)
