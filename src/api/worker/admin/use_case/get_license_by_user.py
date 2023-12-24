from api.worker.admin import DocumentType
from database.repositories import LicenseRepositoryInterface
from database.schemas import LicenseTable


class GetLicenseByUser:
    def __init__(self, license_repository: LicenseRepositoryInterface):
        self.license_repository = license_repository

    def worker(self, user_id: int, document_type: str) -> LicenseTable:
        if user_id < 0 or (document_type != DocumentType.Basic.name and document_type != DocumentType.Driver) :
            raise ValueError()

        return self.license_repository.get_license_by_user_id(user_id, document_type)
