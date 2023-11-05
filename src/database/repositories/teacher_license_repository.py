from abc import ABC
from typing import IO, Any

from psycopg2 import errorcodes
from psycopg2.errors import lookup

from api import log
from database import establishing_connection
from database.exceptions import InternalServer, UniqueViolation
from database.schemas import TeacherLicenseTable, UserTable


class TeacherLicenseRepositoryInterface(ABC):
    @staticmethod
    def insert(document: bytes, user: UserTable) -> TeacherLicenseTable: ...


class TeacherLicenseRepository(TeacherLicenseRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "teacher_license"

    @staticmethod
    def insert(document: bytes, user: UserTable) -> TeacherLicenseTable:
        query = f"""INSERT INTO carmate.{TeacherLicenseRepository.POSTGRES_TABLE_NAME}(license_img, user_id)
                    VALUES (%s, %s)"""

        conn: Any
        try:
            conn = establishing_connection()
        except InternalServer as e:
            log(e)
            raise InternalServer()
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (document, user.id,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    log(e)
                    raise UniqueViolation()
                except Exception as e:
                    log(e)
                    raise InternalServer()
            conn.close()
        return TeacherLicenseTable(document, user.id)
