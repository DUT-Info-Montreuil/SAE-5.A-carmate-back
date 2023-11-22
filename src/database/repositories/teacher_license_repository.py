from abc import ABC
from typing import IO, Any

from psycopg2 import errorcodes
from psycopg2.errors import lookup

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
                    VALUES (%s, %s)
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
                    curs.execute(query, (document, user.id,))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    id = curs.fetchone()[0]
            conn.commit()
            conn.close()
        return TeacherLicenseTable(id, document, user.id)
