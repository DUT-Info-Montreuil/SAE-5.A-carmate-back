import logging
import os

from waitress import serve
from flask import Flask
from flask_cors import CORS

from api.controller import (
    AdminRoutes, 
    AuthRoutes,
)
from database.repositories import (
    TokenRepositoryInterface, 
    UserAdminRepositoryInterface, 
    LicenseRepositoryInterface,
    UserRepositoryInterface,
    LicenseRepository, 
    UserRepository,
    TokenRepository,
    UserAdminRepository,
)
from test.mock import (
    InMemoryLicenseRepository,
    InMemoryUserAdminRepository,
    InMemoryTokenRepository,
    InMemoryUserRepository
)


class Api(object):
    """
    All property about the API
    """
    host = '0.0.0.0'

    logging_level = logging.DEBUG
    logging_format = '[%(levelname)s][%(asctime)s] %(message)s'

    token_repository: TokenRepositoryInterface
    user_repository: UserRepositoryInterface
    user_admin_repository: UserAdminRepositoryInterface
    license_repository = LicenseRepositoryInterface

    def __init__(self) -> None:
        match os.getenv("API_MODE"):
            case "PROD":
                self.postgres()
            case "TEST":
                self.mock()
            case None:
                raise Exception("API_MODE must be set !")
            case _:
                raise Exception(f"Value error in API_MODE ({os.getenv('API_MODE')} invalid)")

        logging.basicConfig(format=self.logging_format,
                            datefmt='%d/%m/%Y %I:%M:%S %p',
                            level=self.logging_level)

        self.api = Flask("carmate-api" if not os.getenv("API_NAME") else os.getenv("API_NAME"))
        self.cors = CORS(self.api, resources={r"*": {"origins": "*"}})

        self.api.register_blueprint(AuthRoutes(self.user_repository, self.token_repository, self.license_repository))
        self.api.register_blueprint(AdminRoutes(self.user_repository, self.user_admin_repository, self.token_repository, self.license_repository))

    def mock(self) -> None:
        self.user_repository = InMemoryUserRepository()
        self.user_admin_repository = InMemoryUserAdminRepository()
        self.token_repository = InMemoryTokenRepository(self.user_repository)
        self.license_repository = InMemoryLicenseRepository(self.user_admin_repository)

    def postgres(self) -> None:
        self.user_repository = UserRepository()
        self.user_admin_repository = UserAdminRepository()
        self.token_repository = TokenRepository()
        self.license_repository = LicenseRepository()

    def run(self) -> None:
        if not os.getenv("API_PORT"):
            raise Exception("API_PORT must be set !")
        self.port = int(os.getenv("API_PORT"))

        match os.getenv("API_MODE"):
            case "PROD":
                serve(self.api,
                      host=self.host,
                      port=self.port)
            case "TEST":
                self.api.run(port=self.port,
                             host=self.host)
            case _:
                error_msg = f"Value {os.getenv('API_MODE')} in API_MODE is invalid !"
                logging.exception(error_msg)
                raise Exception(error_msg)


Api().run()
