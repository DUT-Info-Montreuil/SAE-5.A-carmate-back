from typing import IO, List
from datetime import datetime, timedelta

from api import check_email
from api.worker.auth.exceptions import *
from api.worker.auth.models import CredentialDTO, TokenDTO
from api.worker.auth.use_case.token import Token
from api.worker.user import AccountType
from database.exceptions import UniqueViolation
from database.repositories import UserRepositoryInterface, TokenRepositoryInterface, StudentLicenseRepositoryInterface
from database.repositories.teacher_license_repository import TeacherLicenseRepositoryInterface
from database.schemas import UserTable


class Register(object):
    user_repository: UserRepositoryInterface
    token_repository: TokenRepositoryInterface

    def __init__(self,
                 user_repository: UserRepositoryInterface,
                 token_repository: TokenRepositoryInterface,
                 student_license_repository: StudentLicenseRepositoryInterface = None,
                 teacher_license_repository: TeacherLicenseRepositoryInterface = None):
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.student_license_repository = student_license_repository
        self.teacher_license_repository = teacher_license_repository

    def worker(self,
               credential: CredentialDTO,
               account_type: AccountType,
               document: IO[bytes],
               academic_years: List[datetime] = None) -> TokenDTO:
        """Register an user and return the session token
        
        :return TokenDTO: session token information
        :raise:
            LengthNameTooLong
            EmailFormatInvalid
            AccountAlreadyExist
            InternalServerError
        """
        check_email(credential.email_address)
        if len(credential.last_name) > 255:
            raise LengthNameTooLong(f"{credential.last_name} is too loog")
        elif len(credential.first_name) > 255:
            raise LengthNameTooLong(f"{credential.first_name} is too long")

        user: UserTable
        try:
            user = self.user_repository.insert(credential)
        except UniqueViolation as e:
            raise AccountAlreadyExist(str(e))
        except Exception as e:
            raise InternalServerError(str(e))

        match account_type:
            case AccountType.Student:
                try:
                    self.student_license_repository.insert(document.read(), academic_years, user)
                except Exception as e:
                    raise InternalServerError(str(e))
            case AccountType.Teacher:
                try:
                    self.teacher_license_repository.insert(document.read(), user)
                except Exception as e:
                    raise InternalServerError(str(e))
            case _:
                raise InternalServerError(f"{account_type} can't match in worker")

        token = Token.generate()
        expiration = datetime.now() + timedelta(days=1)
        try:
            self.token_repository.insert(token, expiration, user)
        except Exception as e:
            raise InternalServerError(str(e))
        return TokenDTO(token, expiration, user.id)
