import logging
import os

from waitress import serve
from flask import Flask, Response, jsonify, request

from api.controller import (
    AdminRoutes,
    AuthRoutes,
    MonitoringRoutes,
    ProfilesRoutes
)
from api.controller.carpooling.search import SearchRoutes
from api.controller.carpooling.with_driver_check import CarpoolingWithDriverCheckRoutes
from api.controller.user.user import UserRoutes
from database.repositories import (
    TokenRepositoryInterface,
    UserAdminRepositoryInterface,
    UserBannedRepositoryInterface,
    LicenseRepositoryInterface,
    UserRepositoryInterface,
    DriverProfileRepositoryInterface,
    PassengerProfileRepositoryInterface,
    LicenseRepository,
    UserRepository,
    TokenRepository,
    UserAdminRepository,
    UserBannedRepository,
    DriverProfileRepository,
    PassengerProfileRepository,
    CarpoolingRepositoryInterface,
    CarpoolingRepository
)
from test.mock import (
    InMemoryLicenseRepository,
    InMemoryUserAdminRepository,
    InMemoryUserBannedRepository,
    InMemoryTokenRepository,
    InMemoryUserRepository,
    InMemoryDriverProfileRepository,
    InMemoryPassengerProfileRepository,
    InMemoryCarpoolingRepository
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
    driver_profile_repository: DriverProfileRepositoryInterface
    passenger_profile_repository: PassengerProfileRepositoryInterface
    user_admin_repository: UserAdminRepositoryInterface
    user_banned_repository: UserBannedRepositoryInterface
    license_repository: LicenseRepositoryInterface
    carpooling_repository: CarpoolingRepositoryInterface

    def __init__(self) -> None:
        self.api = Flask("carmate-api" if not os.getenv("API_NAME") else os.getenv("API_NAME"))

        logging.basicConfig(format=self.logging_format,
                            datefmt='%d/%m/%Y %I:%M:%S %p',
                            level=self.logging_level)

        match os.getenv("API_MODE"):
            case "PROD":
                self.postgres()
            case "TEST":
                self.mock()
            case None:
                raise Exception("API_MODE must be set !")
            case _:
                raise Exception(
                    f"Value error in API_MODE ({os.getenv('API_MODE')} invalid)")

        monitoring = MonitoringRoutes()
        auth = AuthRoutes(self.user_repository, self.passenger_profile_repository, self.user_banned_repository, self.user_admin_repository, self.token_repository, self.license_repository)
        profiles = ProfilesRoutes(self.user_repository, self.driver_profile_repository, self.passenger_profile_repository, self.license_repository, self.token_repository, self.user_banned_repository, self.user_admin_repository)
        self.api.register_blueprint(monitoring)
        self.api.register_blueprint(AdminRoutes(self.user_repository, self.user_admin_repository, self.user_banned_repository, self.token_repository, self.license_repository))
        self.api.register_blueprint(profiles)
        self.api.register_blueprint(auth)
        self.api.register_blueprint(UserRoutes(self.user_repository, self.token_repository, self.user_banned_repository, self.user_admin_repository, self.license_repository))
        self.api.register_blueprint(SearchRoutes(self.carpooling_repository))
        self.api.register_blueprint(CarpoolingWithDriverCheckRoutes(self.carpooling_repository, self.token_repository, self.user_banned_repository, self.user_admin_repository, self.license_repository, self.user_repository))

        if os.getenv("API_MODE") == "PROD":
            self.api.after_request(self.handle_preflight_requests)
            self.api.before_request(monitoring.readiness_api)

    def mock(self) -> None:
        self.user_repository = InMemoryUserRepository()
        self.driver_profile_repository = InMemoryDriverProfileRepository()
        self.passenger_profile_repository = InMemoryPassengerProfileRepository()
        self.user_admin_repository = InMemoryUserAdminRepository()
        self.user_banned_repository = InMemoryUserBannedRepository()
        self.token_repository = InMemoryTokenRepository(self.user_repository)
        self.license_repository = InMemoryLicenseRepository(self.user_repository)
        self.carpooling_repository = InMemoryCarpoolingRepository()

    def postgres(self) -> None:
        self.user_repository = UserRepository()
        self.driver_profile_repository = DriverProfileRepository()
        self.passenger_profile_repository = PassengerProfileRepository()
        self.user_admin_repository = UserAdminRepository()
        self.user_banned_repository = UserBannedRepository()
        self.token_repository = TokenRepository()
        self.license_repository = LicenseRepository()
        self.carpooling_repository = CarpoolingRepository()

    def handle_preflight_requests(self, response: Response):
        if request.method == 'OPTIONS':
            response.status_code = 200
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'content-type,authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, HEAD')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Content-Type', 'application/json')
        return response

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
