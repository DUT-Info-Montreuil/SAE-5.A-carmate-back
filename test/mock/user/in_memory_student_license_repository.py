from datetime import datetime
from typing import List

from database.repositories import StudentLicenseRepositoryInterface
from database.schemas import StudentLicenseTable, UserTable


class InMemoryStudentLicenseRepository(StudentLicenseRepositoryInterface):
    student_licenses: List[StudentLicenseTable] = []
    licenses_count: int = 0

    @staticmethod
    def insert(document: bytes,
               academic_years: List[datetime],
               user: UserTable) -> StudentLicenseTable:
        in_memory_student_license = StudentLicenseTable.to_self((InMemoryStudentLicenseRepository.licenses_count, document, academic_years, user.id))
    
        InMemoryStudentLicenseRepository.student_licenses.append(in_memory_student_license)
        InMemoryStudentLicenseRepository.licenses_count = InMemoryStudentLicenseRepository.licenses_count + 1
        return in_memory_student_license
