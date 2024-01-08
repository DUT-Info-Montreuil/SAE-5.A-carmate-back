from abc import ABC
from typing import (
    Dict,
    List,
    Union
)

from api.worker.admin.models import LicenseToValidateDTO, LicenseToValidate
from database.schemas import LicenseTable, UserTable


class LicenseRepositoryInterface(ABC):
    def insert(self,
               document: bytes,
               user: UserTable,
               document_type: str) -> LicenseTable: ...

    def get_licenses_not_validated(self,
                                   page: int | None) -> Dict[str, Union[int, List[LicenseToValidateDTO]]]: ...

    def get_license_not_validated(self,
                                  document_id: int) -> LicenseToValidate: ...

    def get_license_by_user_id(self,
                               user_id: int,
                               document_type: str) -> LicenseTable: ...

    def update_status(self,
                      license_id: int,
                      validation_status: str) -> None: ...

    def get_next_license_id_to_validate(self) -> int: ...
