from typing import List, Dict, Union

from api.worker.admin.models.license_to_validate import LicenseToValidateDTO
from database.repositories import LicenseRepositoryInterface


class GetLicensesToValidate:
    def __init__(self, license_repository: LicenseRepositoryInterface):
        self.license_repository = license_repository

    def worker(self, page: int | None = None) -> Dict[str, Union[int, List[LicenseToValidateDTO]]]:
        if page is not None and page < 1:
            raise ValueError()

        license_to_validate_list: Dict[str, Union[int, List[LicenseToValidateDTO]]]
        license_to_validate_list = self.license_repository.get_licenses_not_validated(page)
        return license_to_validate_list
