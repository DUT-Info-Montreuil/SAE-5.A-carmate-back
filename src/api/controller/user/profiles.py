from datetime import datetime
from hashlib import sha512

from flask import Blueprint, abort, jsonify, request

from api import IMAGE_FORMAT_ALLOWED_EXTENSIONS
from api.exceptions import (
    CredentialInvalid,
    DriverNotFound,
    PassengerNotFound, 
    ProfileAlreadyExist, 
    UserNotFound
)
from api.worker.auth.use_case import CheckToken
from api.worker.user.models import (
    PassengerProfileDTO, 
    DriverProfileDTO
)
from api.worker.user.use_case import (
    CreateDriverProfile,
    CreatePassengerProfile,
    GetPassengerProfile,
    GetDriverProfile
)
from database.repositories import (
    UserRepositoryInterface,
    DriverProfileRepositoryInterface,
    PassengerProfileRepositoryInterface,
    LicenseRepositoryInterface,
    TokenRepositoryInterface
)


class ProfilesRoutes(Blueprint):
    user_repository: UserRepositoryInterface
    driver_profile_repository: DriverProfileRepositoryInterface
    passenger_profile_repository: PassengerProfileRepositoryInterface
    license_repository: LicenseRepositoryInterface
    token_repository: TokenRepositoryInterface 
    
    def __init__(self,
                 user_repository: UserRepositoryInterface,
                 driver_profile_repository: DriverProfileRepositoryInterface,
                 passenger_profile_repository: PassengerProfileRepositoryInterface,
                 license_repository: LicenseRepositoryInterface,
                 token_repository: TokenRepositoryInterface):
        super().__init__("profiles", __name__,
                         url_prefix="/profile")
        
        self.user_repository = user_repository
        self.driver_profile_repository = driver_profile_repository
        self.passenger_profile_repository = passenger_profile_repository
        self.license_repository = license_repository
        self.token_repository = token_repository

        self.before_request(self.token_is_valid)
        self.route("/passenger",
                   methods=["GET"])(self.get_passenger_profile_api)
        self.route("/driver",
                   methods=["GET"])(self.get_driver_profile_api)
        self.route("/passenger",
                   methods=["POST"])(self.create_passenger_profile_api)
        self.route("/driver",
                   methods=["POST"])(self.create_driver_profile_api)

    def extract_token(self, authorization: str):
        if not authorization:
            raise CredentialInvalid()

        authorization_value = authorization.split(" ")
        if len(authorization_value) != 2 or authorization_value[0].lower() != "bearer":
            raise CredentialInvalid()
        return authorization_value[1]
    
    def token_is_valid(self):
        token: str
        try:
            token = self.extract_token(request.headers.get("Authorization"))
        except CredentialInvalid:
            abort(401)
        
        is_token_valid: bool
        try:
            is_token_valid = CheckToken(self.token_repository).worker(token)
        except Exception:
            abort(500)

        if not is_token_valid:
            abort(401)

    def get_passenger_profile_api(self):
        passenger_profile: PassengerProfileDTO = None
        if "passenger_id" in request.args.keys():
            passenger_id: int
            try:
                passenger_id = int(request.args.get("passenger_id"))
            except ValueError:
                abort(400)
            except Exception:
                abort(500)

            try:
                passenger_profile = GetPassengerProfile(self.token_repository,
                                                        self.passenger_profile_repository).worker(passenger_id=passenger_id)
            except PassengerNotFound:
                abort(404)
            except Exception:
                abort(500)
        elif "Authorization" in request.headers.keys():
            try:
                passenger_profile = GetPassengerProfile(self.token_repository,
                                                        self.passenger_profile_repository).worker(token=self.extract_token(request.headers.get("Authorization")))
            except PassengerNotFound:
                abort(404)
            except Exception:
                abort(500)
        
        if not passenger_profile:
            abort(400)
        return passenger_profile

    def get_driver_profile_api(self):
        driver_profile: DriverProfileDTO = None
        if "driver_id" in request.args.keys():
            driver_id: int
            try:
                driver_id = int(request.args.get("driver_id"))
            except ValueError:
                abort(400)
            except Exception:
                abort(500)

            try:
                driver_profile = GetDriverProfile(self.token_repository,
                                                  self.driver_profile_repository).worker(driver_id=driver_id)
            except DriverNotFound:
                abort(404)
            except Exception:
                abort(500)
        elif "Authorization" in request.headers.keys():
            try:
                driver_profile = GetDriverProfile(self.token_repository,
                                                  self.driver_profile_repository).worker(token=self.extract_token(request.headers.get("Authorization")))
            except DriverNotFound:
                abort(404)
            except Exception:
                abort(500)
        
        if not driver_profile:
            abort(400)
        return driver_profile

    def create_passenger_profile_api(self):
        if request.is_json:
            abort(415)

        passenger_id: int
        try:
            passenger_id = CreatePassengerProfile(self.token_repository,
                                                  self.passenger_profile_repository).worker(self.extract_token(request.headers.get("Authorization")).digest())
        except ProfileAlreadyExist:
            abort(409)
        except UserNotFound:
            abort(404)
        except CredentialInvalid:
            abort(401)
        except Exception:
            abort(500)
        return jsonify({"passenger_id": passenger_id})

    def create_driver_profile_api(self):
        if request.is_json:
            abort(415)

        if "document" not in request.files:
            abort(415)
        document = request.files["document"]
        # Check file extension of the document if it matches a file extension of an image
        if not all(["." in document.filename, document.filename.rsplit(".", 1)[1].lower() in IMAGE_FORMAT_ALLOWED_EXTENSIONS]):
            abort(415)

        driver_id: int
        try:
            driver_id = CreateDriverProfile(self.token_repository,
                                            self.driver_profile_repository,
                                            self.license_repository).worker(self.extract_token(request.headers.get("Authorization")),
                                                                            document.stream)
        except ProfileAlreadyExist:
            abort(409)
        except UserNotFound:
            abort(404)
        except CredentialInvalid:
            abort(401)
        except Exception:
            abort(500)
        return jsonify({"driver_id": driver_id})