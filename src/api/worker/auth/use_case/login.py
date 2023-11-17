import re

from datetime import datetime, timedelta
from hashlib import sha512

from api.worker.auth.exceptions import EmailFormatInvalid, InternalServerError
from api.worker.auth.models.credential_dto import CredentialDTO
from api.worker.auth.models.token_dto import TokenDTO
from api.worker.auth.use_case.token import Token
from database.repositories import UserRepositoryInterface
from database.repositories.token_repository import TokenRepositoryInterface
from database.exceptions import CredentialInvalid, InternalServer, NotFound


class Login:

    user_repository: UserRepositoryInterface
    token_repository: TokenRepositoryInterface

    def __init__(self,
                 user_repository: UserRepositoryInterface,
                 token_repository: TokenRepositoryInterface):
        self.user_repository = user_repository
        self.token_repository = token_repository

    def worker(self, credential: CredentialDTO) -> TokenDTO:
        """ Manages the authentication process.

        This method handles the authentication process by verifying the credentials
        provided in the CredentialDTO object. It performs the following steps:
            - Checks the email format.
            - Retrieves user-related data using the email provided.
            - Checks whether the password supplied matches the password registered for the user.
            - Creates a valid authentication token and inserts it into the database.
            - Returns a TokenDTO object containing the generated token information.

        :param credential (CredentialDTO): The credentials provided.

        :raises:
            EmailFormatInvalid: if credential.email_adress is invalid.
            CredentialInvalid: if credentials are invalid.
            InternalServerError: In the event of an internal error when inserting the token into the database.
        :return: TokenDTO: An object representing the generated authentication token.
        """
        # Checks the email format.
        if not re.match(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', credential.email_address):
            raise EmailFormatInvalid()

        # Retrieves user-related data using the email provided.
        try:
            user = self.user_repository.get_user_by_email(credential.email_address)
        except InternalServer:
            raise InternalServerError()
        except NotFound:
            raise CredentialInvalid()
        except Exception:
            raise InternalServerError()

        # Checks whether the password supplied matches the password registered for the user.
        if sha512(credential.password.encode('utf-8')).hexdigest() != user.password:
            raise CredentialInvalid()

        # Creates a valid authentication token and inserts it into the database.
        token: str = Token.generate()
        expiration: datetime = datetime.now() + timedelta(days=1)
        try:
            self.token_repository.insert(token, expiration, user)
        except Exception as e:
            raise InternalServerError()

        # Returns a TokenDTO object containing the generated token information.
        return TokenDTO(token, expiration, user.id)
