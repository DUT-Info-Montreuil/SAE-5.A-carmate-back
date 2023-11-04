from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class CredentialDTO:
    first_name: str
    last_name: str
    email_address: str
    password: str

    @staticmethod
    def json_to_self(json: dict) -> Self:
        return CredentialDTO(
            json["first_name"],
            json["last_name"],
            json["email_address"],
            json["password"]
        )

    @staticmethod
    def tuple_to_self(_tuple: tuple) -> Self:
        return CredentialDTO(
            _tuple[0],
            _tuple[1],
            _tuple[2],
            _tuple[3]
        )

    def to_json(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email_address": self.email_address,
            "password": self.password,
        }