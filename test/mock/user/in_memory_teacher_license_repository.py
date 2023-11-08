from typing import List

from database.repositories import TeacherLicenseRepositoryInterface
from database.schemas import TeacherLicenseTable, UserTable


class InMemoryTeacherLicenseRepository(TeacherLicenseRepositoryInterface):
    teacher_licenses: List[TeacherLicenseTable] = []
    licenses_count: int = 0

    @staticmethod
    def insert(document: bytes,
               user: UserTable) -> TeacherLicenseTable:
        in_memory_teacher_license = TeacherLicenseTable.to_self((InMemoryTeacherLicenseRepository.licenses_count, document, user.id))
        
        InMemoryTeacherLicenseRepository.teacher_licenses.append(in_memory_teacher_license)
        InMemoryTeacherLicenseRepository.licenses_count = InMemoryTeacherLicenseRepository.licenses_count + 1
        return in_memory_teacher_license

