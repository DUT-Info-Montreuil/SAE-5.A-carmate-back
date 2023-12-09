import secrets

from datetime import datetime, timedelta
from hashlib import sha512

from api import check_email
from api.worker.auth.use_case import Token
from api.exceptions import (
    BannedAccount, 
    CredentialInvalid, 
    InternalServerError
)
from api.worker.auth.models import (
    CredentialDTO, 
    TokenDTO
)
from database.exceptions import NotFound
from database.schemas import UserTable
from database.repositories import (
    UserRepositoryInterface,
    TokenRepositoryInterface,
    UserBannedRepositoryInterface
)


class Login:
    user_repository: UserRepositoryInterface
    user_banned_repository: UserBannedRepositoryInterface
    token_repository: TokenRepositoryInterface

    def __init__(self,
                 user_repository: UserRepositoryInterface,
                 user_banned_repository: UserBannedRepositoryInterface,
                 token_repository: TokenRepositoryInterface):
        self.user_repository = user_repository
        self.user_banned_repository = user_banned_repository
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
        check_email(credential.email_address)

        # Retrieves user-related data using the email provided.
        user: UserTable
        try:
            user = self.user_repository.get_user_by_email(credential.email_address)
        except NotFound as e:
            raise CredentialInvalid()
        except Exception as e:
            raise InternalServerError(str(e))
        
        is_banned: bool
        try:
            is_banned = self.user_banned_repository.is_banned(user.id)
        except Exception as e:
            raise InternalServerError(str(e))
        if is_banned:
            raise BannedAccount(f"{user.id} is banned")

        if not secrets.compare_digest(sha512(credential.password.encode('utf-8')).digest(), user.password):
            raise CredentialInvalid()

        token = Token.generate()
        expiration = datetime.now() + timedelta(days=1)
        try:
            self.token_repository.insert(token, expiration, user)
        except Exception as e:
            raise InternalServerError(str(e))

        return TokenDTO(token, expiration, user.id)
