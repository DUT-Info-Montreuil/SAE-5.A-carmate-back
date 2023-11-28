from datetime import datetime
from typing import List

from database.repositories import LicenseRepositoryInterface
from database.schemas import StudentLicenseTable, UserTable


class InMemoryLicenseRepository(LicenseRepositoryInterface):
    student_licenses: List[StudentLicenseTable] = []
    licenses_count: int = 0

    @staticmethod
    def insert(document: bytes,
               user: UserTable) -> StudentLicenseTable:
        in_memory_student_license = StudentLicenseTable.to_self((InMemoryLicenseRepository.licenses_count, document, user.id))
    
        InMemoryLicenseRepository.student_licenses.append(in_memory_student_license)
        InMemoryLicenseRepository.licenses_count = InMemoryLicenseRepository.licenses_count + 1
        return in_memory_student_license
