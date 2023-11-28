from datetime import datetime
from typing import List, Dict, Union

from api.worker.admin import ValidationStatus
from api.worker.admin.models import LicenseToValidateDTO, LicenseToValidate
from database.exceptions import NotFound, DocumentAlreadyChecked
from database.repositories import LicenseRepositoryInterface
from database.schemas import LicenseTable, UserTable


class InMemoryLicenseRepository(LicenseRepositoryInterface):
    def __init__(self, user_repo = None):
        self.user_repo = user_repo
        self.licenses: List[LicenseTable] = []
        self.licenses_count = 0

    def insert(self, document: bytes,
               user: UserTable,
               document_type: str) -> LicenseTable:

        in_memory_student_license = LicenseTable.to_self((self.licenses_count, document, document_type, ValidationStatus.Pending.name, datetime.now(), user.id))

        self.licenses.append(in_memory_student_license)
        self.licenses_count = self.licenses_count + 1
        return in_memory_student_license

    def get_licenses_not_validated(self, page: int | None) -> Dict[str, Union[int, List[LicenseToValidateDTO]]]:
        if self.user_repo is None:
            raise Exception("The function get_licenses_not_validated won't work without user repository")

        list_license_to_validate: List[LicenseToValidateDTO] = []
        licenses_not_validated = list(filter(lambda lic: lic.validation_status is ValidationStatus.Pending.name, self.licenses))

        elements_per_page = 30

        start_index = (page - 1) * elements_per_page if page is not None else 0
        end_index = start_index + elements_per_page

        for license_not_validated in licenses_not_validated[start_index:end_index]:
            matching_user = next((user for user in self.user_repo.users if user.id == license_not_validated.user_id), None)
            if matching_user is None:
                raise Exception("A license is linked to a non-existent user")
            else:
                list_license_to_validate.append(
                    LicenseToValidateDTO(
                        matching_user.first_name,
                        matching_user.last_name,
                        matching_user.account_status,
                        datetime.now(),
                        license_not_validated.document_type,
                        license_not_validated.id,
                    )
                )

        return {
            "nb_documents": len(self.licenses),
            "items": list_license_to_validate
        }

    def get_license_not_validated(self, document_id: int) -> LicenseToValidate:
        if self.user_repo is None:
            raise Exception("The function get_licenses_not_validated won't work without user repository")

        license_to_validate: LicenseToValidate | None = None
        document_found: LicenseTable | None = None
        user_found: UserTable | None = None

        for document in self.licenses:
            if document.id == document_id:
                document_found = document

        if document_found is None:
            raise NotFound("document not found")

        if document_found.validation_status != ValidationStatus.Pending.name:
            raise DocumentAlreadyChecked("document is already checked")

        for user in self.user_repo.users:
            if user.id == document_found.user_id:
                user_found = user

        if user_found is None:
            raise Exception("The user linked to the document doesn't exists")

        license_to_validate = LicenseToValidate.tuple_to_self((
            user_found.first_name,
            user_found.last_name,
            user_found.account_status,
            document_found.created_at,
            document_found.document_type,
            document_found.license_img
        ))

        return license_to_validate
