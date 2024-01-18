from api.worker import Worker
from api.worker.admin.models import LicenseToValidate


class GetLicenseToValidate(Worker):
    def worker(self, 
               document_id: int | None = None) -> LicenseToValidate:
        if document_id is None:
            raise ValueError()

        license_to_validate_list = self.license_repository.get_license_not_validated(document_id)
        return license_to_validate_list
