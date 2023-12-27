from api.worker import Worker
from api.worker.admin import DocumentType
from database.schemas import LicenseTable


class GetLicenseByUser(Worker):
    def worker(self, 
               user_id: int, 
               document_type: str) -> LicenseTable:
        if user_id < 0 \
            or (document_type != DocumentType.Basic.name \
                and document_type != DocumentType.Driver) :
            raise ValueError()

        return self.license_repository.get_license_by_user_id(user_id, document_type)
