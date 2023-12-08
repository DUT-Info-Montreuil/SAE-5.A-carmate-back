from abc import ABC
from typing import Any, List, Union, Dict

from psycopg2 import errorcodes
from psycopg2.errors import lookup, ProgrammingError, InvalidTextRepresentation

from api.worker.admin import ValidationStatus
from api.worker.admin.models import LicenseToValidateDTO, LicenseToValidate
from database import establishing_connection
from database.exceptions import InternalServer, InvalidInputEnumValue, NotFound, UniqueViolation, DocumentAlreadyChecked
from database.repositories import UserRepository
from database.schemas import LicenseTable, UserTable


class LicenseRepositoryInterface(ABC):
    def insert(self,
               document: bytes,
               user: UserTable,
               document_type: str) -> LicenseTable: ...

    def get_licenses_not_validated(self, page: int | None) -> Dict[str, Union[int, List[LicenseToValidateDTO]]]: ...

    def get_license_not_validated(self, document_id: int) -> LicenseToValidate: ...

    def update_status(self, 
                      license_id: int,
                      validation_status: str) -> None: ...

    def get(self, license_id: int) -> LicenseTable: ...

class LicenseRepository(LicenseRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "license"

    def insert(self,
               document: bytes,
               user: UserTable,
               document_type) -> LicenseTable:
        query = f"""INSERT INTO carmate.{LicenseRepository.POSTGRES_TABLE_NAME}
                    VALUES (DEFAULT, %s, %s, DEFAULT, DEFAULT, %s)
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
                    curs.execute(query, (document.read(), document_type, user.id))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    id = curs.fetchone()[0]
            conn.commit()
            conn.close()
        return LicenseTable(id, document.read(), False, user.id)

    def get_licenses_not_validated(self, page: int | None) -> Dict[str, Union[int, List[LicenseToValidateDTO]]]:
        offset = (page - 1) * 30 if page is not None else 0
        query = f"""SELECT ur.first_name, ur.last_name, ur.account_status, lr.published_at, lr.document_type, lr.id
                    FROM carmate.{LicenseRepository.POSTGRES_TABLE_NAME} lr
                    INNER JOIN carmate."{UserRepository.POSTGRES_TABLE_NAME}" ur ON lr.user_id = ur.id
                    WHERE validation_status = 'Pending'
                    LIMIT 30
                    OFFSET {offset}"""
        count_query = f"""SELECT COUNT(*)
                    FROM carmate.{LicenseRepository.POSTGRES_TABLE_NAME}
                    WHERE validation_status = 'Pending'"""

        conn: Any
        try:
            conn = establishing_connection()
        except InternalServer as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query)
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    license_rows = curs.fetchall()
                try:
                    curs.execute(count_query)
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    count = curs.fetchone()
            conn.close()
        return {
            "nb_documents": count,
            "items": [LicenseToValidateDTO(*tpl) for tpl in license_rows]
        }

    def get_license_not_validated(self, document_id: int) -> LicenseToValidate:
        query = f"""SELECT ur.first_name, ur.last_name, ur.account_status, lr.published_at, lr.document_type, lr.license_img, lr.validation_status
                    FROM carmate.{LicenseRepository.POSTGRES_TABLE_NAME} lr
                    INNER JOIN carmate."{UserRepository.POSTGRES_TABLE_NAME}" ur ON lr.user_id = ur.id
                    WHERE lr.id = %s"""

        conn: Any
        try:
            conn = establishing_connection()
        except InternalServer as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (document_id, ))
                except ProgrammingError:
                    print("lll")
                    raise NotFound("document not found")
                except IndexError:
                    print("lllll")
                    raise NotFound("document not found")
                except Exception as e:
                    raise InternalServer(str(e))
                else:
                    found_license = curs.fetchone()

                    if not found_license:
                        raise NotFound("document not found")
            conn.close()

        if found_license[6] != ValidationStatus.Pending.name:
            raise DocumentAlreadyChecked("document is already checked")

        return LicenseToValidate.tuple_to_self(found_license)

    def update_status(self, license_id: int, validation_status: str) -> None:
        query = f"""UPDATE carmate.{LicenseRepository.POSTGRES_TABLE_NAME}
                    SET validation_status=%s
                    WHERE id=%s"""
        
        conn: Any
        try:
            conn = establishing_connection()
        except InternalServer as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (validation_status, license_id,))
                except InvalidTextRepresentation as e:
                    raise InvalidInputEnumValue(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                
                if curs.rowcount == 0:
                    raise NotFound("license not found, can't update")
            conn.commit()
            conn.close()

    def get(self, license_id: int) -> LicenseTable:
        query = f"""SELECT * 
                    FROM carmate.{LicenseRepository.POSTGRES_TABLE_NAME}
                    WHERE id=%s"""
        
        conn: Any
        found_license: LicenseTable
        try:
            conn = establishing_connection()
        except InternalServer as e:
            raise InternalServer(str(e))
        else:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (license_id,))
                    found_license = LicenseTable.to_self(curs.fetchone())
                except TypeError:
                    raise NotFound("license not found")
                except ProgrammingError:
                    raise NotFound("license not found")
                except Exception as e:
                    raise InternalServer(str(e))
            conn.close()
        
        return found_license
