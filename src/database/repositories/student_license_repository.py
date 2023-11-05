from abc import ABC
from datetime import datetime
from typing import Any, List

from psycopg2 import errorcodes
from psycopg2.errors import lookup

from api import log
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
                    VALUES (%s, %s, %s)"""

        conn: Any
        try:
            conn = establishing_connection()
        except InternalServer as e:
            log(e)
            raise InternalServer()
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (document.read(), academic_years, user.id,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    log(e)
                    raise UniqueViolation()
                except Exception as e:
                    log(e)
                    raise InternalServer()
            conn.close()
        return StudentLicenseTable(document.read(), academic_years, user.id)
