from typing import List, Dict, Union

from api.worker import Worker
from api.worker.admin.models import LicenseToValidateDTO


class GetLicensesToValidate(Worker):
    def worker(self, 
               page: int | None = None) -> Dict[str, Union[int, List[LicenseToValidateDTO]]]:
        if page is not None \
            and page < 1:
            raise ValueError()

        license_to_validate_list: Dict[str, Union[int, List[LicenseToValidateDTO]]]
        license_to_validate_list = self.license_repository.get_licenses_not_validated(page)
        return license_to_validate_list
