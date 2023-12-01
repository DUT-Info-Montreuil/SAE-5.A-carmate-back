
from database.repositories import LicenseRepositoryInterface
from api.worker.admin.models.license_to_validate import LicenseToValidate


class GetLicenseToValidate:
    def __init__(self, license_repository: LicenseRepositoryInterface):
        self.license_repository = license_repository

    def worker(self, document_id: int | None = None) -> LicenseToValidate:
        if document_id is None:
            raise ValueError()

        license_to_validate_list = self.license_repository.get_license_not_validated(document_id)
        return license_to_validate_list
