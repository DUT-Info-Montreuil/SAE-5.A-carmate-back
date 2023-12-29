from flask import Blueprint, abort, jsonify, request

from api import IMAGE_FORMAT_ALLOWED_EXTENSIONS
from api.controller import extract_token
from api.exceptions import (
    CredentialInvalid,
    DriverNotFound,
    PassengerNotFound, 
    ProfileAlreadyExist, 
    UserNotFound
)
from api.worker.auth.models import UserInformationDTO
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


class ProfilesRoutes(Blueprint):
    def __init__(self):
        super().__init__("profiles", __name__,
                         url_prefix="/profile")
        
        self.before_request(self.token_is_valid)
        self.route("/passenger",
                   methods=["GET"])(self.get_passenger_profile_api)
        self.route("/driver",
                   methods=["GET"])(self.get_driver_profile_api)
        self.route("/passenger",
                   methods=["POST"])(self.create_passenger_profile_api)
        self.route("/driver",
                   methods=["POST"])(self.create_driver_profile_api)

    def token_is_valid(self):
        token: str
        try:
            token = extract_token()
        except CredentialInvalid:
            abort(401)
        
        user_infos: None | UserInformationDTO
        try:
            user_infos = CheckToken().worker(token)
        except Exception:
            abort(500)

        if not user_infos:
            abort(401)
        if user_infos.banned:
            abort(403)

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
                passenger_profile = GetPassengerProfile().worker(passenger_id=passenger_id)
            except PassengerNotFound:
                abort(404)
            except Exception:
                abort(500)
        elif "Authorization" in request.headers.keys():
            try:
                passenger_profile = GetPassengerProfile().worker(token=extract_token())
            except PassengerNotFound:
                abort(404)
            except Exception:
                abort(500)
        
        if not passenger_profile:
            abort(400)
        return jsonify(passenger_profile.to_json())

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
                driver_profile = GetDriverProfile().worker(driver_id=driver_id)
            except DriverNotFound:
                abort(404)
            except Exception:
                abort(500)
        elif request.authorization is not None:
            try:
                driver_profile = GetDriverProfile().worker(token=extract_token())
            except DriverNotFound:
                abort(404)
            except Exception:
                abort(500)
        
        if driver_profile is None:
            abort(400)
        return jsonify(driver_profile.to_json())

    def create_passenger_profile_api(self):
        if request.is_json:
            abort(415)

        passenger_id: int
        try:
            passenger_id = CreatePassengerProfile().worker(extract_token())
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

        driver: DriverProfileDTO
        try:
            driver = CreateDriverProfile().worker(extract_token(),
                                                  document.stream)
        except ProfileAlreadyExist:
            abort(409)
        except UserNotFound:
            abort(404)
        except CredentialInvalid:
            abort(401)
        except Exception:
            abort(500)
        return jsonify({"driver_id": driver.id})
