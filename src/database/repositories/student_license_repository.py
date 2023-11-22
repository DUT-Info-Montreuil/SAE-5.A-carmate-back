from abc import ABC
from datetime import datetime
from typing import Any, List

from psycopg2 import errorcodes
from psycopg2.errors import lookup

from database import establishing_connection
from database.exceptions import InternalServer, UniqueViolation
from database.schemas import StudentLicenseTable, UserTable


class StudentLicenseRepositoryInterface(ABC):
    @staticmethod
    def insert(document: bytes,
               academic_years: List[datetime],
               user: UserTable) -> StudentLicenseTable: ...


class StudentLicenseRepository(StudentLicenseRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "student_license"

    @staticmethod
    def insert(document: bytes,
               academic_years: List[datetime],
               user: UserTable) -> StudentLicenseTable:
        query = f"""INSERT INTO carmate.{StudentLicenseRepository.POSTGRES_TABLE_NAME}(license_img, academic_years, user_id)
                    VALUES (%s, %s, %s)
                    RETURNING id"""

        id: int
        conn: Any
        try:
            conn = establishing_connection()
        except InternalServer as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (document.read(), academic_years, user.id,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    id = curs.fetchone()[0]
            conn.commit()
            conn.close()
        return StudentLicenseTable(id, document.read(), academic_years, user.id)
