from typing import IO
from datetime import datetime, timedelta

from api import check_email
from api.worker import Worker
from api.worker.auth import Token
from api.worker.auth.models import CredentialDTO, TokenDTO
from api.worker.user import AccountStatus
from api.worker.admin import DocumentType
from api.exceptions import (
    LengthNameTooLong, 
    AccountAlreadyExist, 
    InternalServerError
)
from database.schemas import UserTable
from database.exceptions import UniqueViolation


class Register(Worker):
    def worker(self,
               credential: CredentialDTO,
               account_status: AccountStatus,
               document: IO[bytes]) -> TokenDTO:
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
            user = self.user_repository.insert(credential, account_status)
        except UniqueViolation as e:
            raise AccountAlreadyExist(str(e))
        except Exception as e:
            raise InternalServerError(str(e))

        try:
            self.license_repository.insert(document.read(), user, DocumentType.Basic.name)
        except Exception as e:
            raise InternalServerError(str(e))

        token = Token.generate()
        expiration = datetime.now() + timedelta(days=1)
        try:
            self.token_repository.insert(token, expiration, user)
        except Exception as e:
            raise InternalServerError(str(e))
        return TokenDTO(token, expiration, user.id)
