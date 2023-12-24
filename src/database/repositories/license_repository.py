from abc import ABC
from datetime import datetime
from typing import List, Union, Dict

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

    def get_licenses_not_validated(self, 
                                   page: int | None) -> Dict[str, Union[int, List[LicenseToValidateDTO]]]: ...

    def get_license_not_validated(self, 
                                  document_id: int) -> LicenseToValidate: ...

    def get_license_by_user_id(self, user_id: int, document_type: str) -> LicenseTable: ...

    def update_status(self, 
                      license_id: int,
                      validation_status: str) -> None: ...

    def get_next_license_id_to_validate(self) -> int: ...


class LicenseRepository(LicenseRepositoryInterface):
    POSTGRES_TABLE_NAME: str = "license"

    def insert(self,
               document: bytes,
               user: UserTable,
               document_type: str) -> LicenseTable:
        query = f"""
            INSERT INTO carmate.{self.POSTGRES_TABLE_NAME}
            VALUES (DEFAULT, %s, %s, DEFAULT, DEFAULT, %s)
            RETURNING id, validation_status, published_at
        """

        id: int
        validation_status: str
        published_at: datetime
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (document, document_type, user.id))
                except lookup(errorcodes.UNIQUE_VIOLATION) as e:
                    raise UniqueViolation(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                id, validation_status, published_at = curs.fetchone()
        return LicenseTable(id, document, document_type, validation_status, published_at, user.id)

    def get_licenses_not_validated(self, page: int | None) -> Dict[str, Union[int, List[LicenseToValidateDTO]]]:
        query = f"""
            SELECT ur.first_name, ur.last_name, ur.account_status, lr.published_at, lr.document_type, lr.id
            FROM carmate.{self.POSTGRES_TABLE_NAME} lr
            INNER JOIN carmate."{UserRepository.POSTGRES_TABLE_NAME}" ur 
                ON lr.user_id=ur.id
            WHERE validation_status='Pending'
            LIMIT 30
            OFFSET {(page - 1) * 30 if page is not None else 0}
        """
        nb_documents_query = f"""
            SELECT COUNT(*)
            FROM carmate.{self.POSTGRES_TABLE_NAME}
            WHERE validation_status='Pending'
        """

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query)
                except Exception as e:
                    raise InternalServer(str(e))
                license_rows = curs.fetchall()

                try:
                    curs.execute(nb_documents_query)
                except Exception as e:
                    raise InternalServer(str(e))
                nb_documents = curs.fetchone()

        return {
            "nb_documents": nb_documents,
            "items": [LicenseToValidateDTO(*tpl) for tpl in license_rows]
        }

    def get_license_not_validated(self, document_id: int) -> LicenseToValidate:
        query = f"""
            SELECT ur.first_name, ur.last_name, ur.account_status, lr.published_at, lr.document_type, lr.license_img, lr.validation_status
            FROM carmate.{LicenseRepository.POSTGRES_TABLE_NAME} lr
            INNER JOIN carmate."{UserRepository.POSTGRES_TABLE_NAME}" ur 
                ON lr.user_id=ur.id
            WHERE lr.id=%s
        """

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (document_id, ))
                except ProgrammingError:
                    raise NotFound("document not found")
                except IndexError:
                    raise NotFound("document not found")
                except Exception as e:
                    raise InternalServer(str(e))
                found_license = curs.fetchone()

        if found_license is None:
            raise NotFound("document not found")
        if found_license[6] != ValidationStatus.Pending.name:
            raise DocumentAlreadyChecked("document is already checked")
        return LicenseToValidate.tuple_to_self(found_license)

    def update_status(self, license_id: int, validation_status: str) -> None:
        query = f"""
            UPDATE carmate.{LicenseRepository.POSTGRES_TABLE_NAME}
            SET validation_status=%s
            WHERE id=%s
        """

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (validation_status, license_id,))
                except InvalidTextRepresentation as e:
                    raise InvalidInputEnumValue(str(e))
                except Exception as e:
                    raise InternalServer(str(e))
                if curs.rowcount == 0:
                    raise NotFound("license not found, can't update")

    def get_next_license_id_to_validate(self) -> int:
        query = f"""
            SELECT lr.id
            FROM carmate.{LicenseRepository.POSTGRES_TABLE_NAME} lr
            INNER JOIN carmate."{UserRepository.POSTGRES_TABLE_NAME}" ur 
                ON lr.user_id = ur.id
            WHERE validation_status = 'Pending'
            LIMIT 1
        """

        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query)
                except TypeError:
                    raise NotFound("No more licenses to validate")
                except ProgrammingError:
                    raise NotFound("No more licenses to validate")
                except Exception as e:
                    raise InternalServer(str(e))
                next_id = curs.fetchone()

        if next_id is not None and len(next_id) > 0:
            return next_id[0]
        raise NotFound("No more licenses to validate")

    def get_license_by_user_id(self, user_id: int, document_type: str) -> LicenseTable:
        query = f"""
            SELECT *
            FROM carmate.{LicenseRepository.POSTGRES_TABLE_NAME} AS lr
            INNER JOIN carmate."{UserRepository.POSTGRES_TABLE_NAME}" AS ur 
                ON lr.user_id=ur.id
            WHERE document_type=%s 
                AND user_id=%s
        """

        license_table: tuple | None
        with establishing_connection() as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (document_type, user_id))
                except TypeError:
                    raise NotFound("License not found")
                except ProgrammingError:
                    raise NotFound("License not found")
                license_table = curs.fetchone()

        if license_table is None:
            raise NotFound("License not found")
        return LicenseTable.to_self(license_table)
