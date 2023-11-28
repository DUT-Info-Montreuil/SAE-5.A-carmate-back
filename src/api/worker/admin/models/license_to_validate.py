import base64
from datetime import datetime
from typing import Self
from dataclasses import dataclass


@dataclass(frozen=True)
class LicenseToValidate:
    first_name: str
    last_name: str
    account_type: str
    published_at: datetime
    license_type: str
    document: bytes

    @staticmethod
    def tuple_to_self(_tuple: tuple):
        return LicenseToValidate(
            _tuple[0],
            _tuple[1],
            _tuple[2],
            _tuple[3],
            _tuple[4],
            _tuple[5],
        )

    def to_json(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "account_type": self.account_type,
            "published_at": self.published_at,
            "license_type": self.license_type,
            "document": base64.encodebytes(self.document).decode('ascii')
        }


@dataclass(frozen=True)
class LicenseToValidateDTO:
    first_name: str
    last_name: str
    account_type: str
    published_at: datetime
    license_type: str
    document_id: int

    @staticmethod
    def tuple_to_self(_tuple: tuple):
        return LicenseToValidateDTO(
            _tuple[0],
            _tuple[1],
            _tuple[2],
            _tuple[3],
            _tuple[4],
            _tuple[5],
        )

    def to_json(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "account_type": self.account_type,
            "document_type": self.license_type,
            "document_id": self.document_id
        }
