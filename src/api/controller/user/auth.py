from flask import Blueprint, abort, jsonify, request, Response

from api import IMAGE_FORMAT_ALLOWED_EXTENSIONS
from api.worker.user import AccountStatus
from api.worker.auth.models import TokenDTO, CredentialDTO, UserInformationDTO
from api.exceptions import AccountAlreadyExist, BannedAccount, CredentialInvalid, LengthNameTooLong, ProfileAlreadyExist, UserNotFound
from api.worker.auth.use_case import Register, Login, CheckToken
from api.worker.user.use_case.create_passenger_profile import CreatePassengerProfile
from database.repositories import (
    TokenRepositoryInterface,
    UserRepositoryInterface,
    PassengerProfileRepositoryInterface,
    UserBannedRepositoryInterface,
    UserAdminRepositoryInterface,
    LicenseRepositoryInterface
)


class AuthRoutes(Blueprint):
    user_repository: UserRepositoryInterface
    passenger_profile_repository: PassengerProfileRepositoryInterface
    user_banned_repository: UserBannedRepositoryInterface
    user_admin_repository: UserAdminRepositoryInterface
    token_repository: TokenRepositoryInterface
    license_repository: LicenseRepositoryInterface

    def __init__(self,
                 user_repository: UserRepositoryInterface,
                 passenger_profile_repository: PassengerProfileRepositoryInterface,
                 user_banned_repository: UserBannedRepositoryInterface,
                 user_admin_repository: UserAdminRepositoryInterface,
                 token_repository: TokenRepositoryInterface,
                 license_repository: LicenseRepositoryInterface):
        super().__init__("auth", __name__,
                         url_prefix="/auth")

        self.token_repository = token_repository
        self.user_repository = user_repository
        self.passenger_profile_repository = passenger_profile_repository
        self.user_banned_repository = user_banned_repository
        self.user_admin_repository = user_admin_repository
        self.license_repository = license_repository

        self.route("/check-token",
                   methods=["POST"])(self.check_token_api)
        self.route("/login",
                   methods=["POST"])(self.login_api)
        self.route("/register",
                   methods=["POST"])(self.register_api)
        self.after_request(self.create_passenger_profile_api)

    def create_passenger_profile_api(self, response: Response):
        if "register" in request.endpoint and response.status_code == 200:
            data = response.json
            try:
                CreatePassengerProfile(self.token_repository,
                                        self.passenger_profile_repository).worker(data["token"])
            except ProfileAlreadyExist:
                abort(409)
            except UserNotFound:
                abort(404)
            except CredentialInvalid:
                abort(401)
            except Exception:
                abort(500)
        return response

    def check_token_api(self) -> Response:
        if not request.is_json:
            abort(415)

        token: str
        try:
            token = request.get_json()["token"]
        except KeyError:
            abort(400)
        except Exception:
            abort(500)

        user_info: None | UserInformationDTO
        try:
            user_info = CheckToken(self.token_repository, 
                                   self.user_banned_repository, 
                                   self.user_admin_repository,
                                   self.license_repository).worker(token)
        except Exception:
            abort(500)

        if not user_info:
            return '', 401
        return jsonify(user_info.to_json())

    def login_api(self) -> Response:
        """Manages the authentication process.
            This method handles the authentication process by verifying the credentials
            provided in the CredentialDTO object. It performs the following steps:
                - Checks the request is json type
                - Get json's data
                - Create CredentialDTO object based on json's data
                - Checks that the attributes of the json request match
                - Try login the user
                - Return the token provided by the login worker
            :param: json: email_adress and password provided by the front form
            :raises:
                - 415: if the request is not json type
                - 400: if credential's attributes are missing
                - 401: CredentialInvalid exception
                - 403: BannedAccount exception
                - 500: InternalServerError (other)
            :return: Response: A JSON response containing the authentication token or an error message.
        """
        if not request.is_json:
            abort(415)

        credential: dict
        try:
            json_data = request.get_json()
            credential = {
                "first_name": "",
                "last_name": "",
                "email_address": json_data["email_address"],
                "password": json_data["password"]
            }
        except KeyError:
            abort(400)
        except Exception:
            abort(500)

        token: TokenDTO
        try:
            token = Login(self.user_repository,
                          self.user_banned_repository,
                          self.token_repository).worker(CredentialDTO.json_to_self(credential))
        except CredentialInvalid:
            abort(401)
        except BannedAccount:
            abort(403)
        except Exception:
            abort(500)
        return jsonify(token.to_json())

    def register_api(self) -> Response:
        """Register an user and return the session token

        :return Response: session token
        :raise:
            400: Bad Request
                - When the type of account is not specified
                - When have missing key in json credential
                - When the first_name or last_name is too long
            409: Conflict
                - When the user already exist
            415: Unsupported Media Type
                - When the content-type is not a multipart/form-data
                - When the filename of the document is invalid or missing
                - When the document is not an image
                - When don't have credential key in multipart/form-data
            500: Internal Server Error
        """
        if "multipart/form-data" not in request.content_type :
            abort(415)

        credential: dict
        account_status: AccountStatus
        try:
            credential = {
                "first_name": request.form.get("first_name"),
                "last_name": request.form.get("last_name"),
                "email_address": request.form.get("email_address"),
                "password": request.form.get("password"),
                "type": request.form.get("type")
            }
            account_status = AccountStatus[credential["type"]]
        except ValueError:
            abort(400)
        except KeyError:
            abort(400)
        except Exception:
            abort(500)
        if any([value is None for value in credential.values()]):
            abort(400)

        if "document" not in request.files:
            abort(415)
        document = request.files["document"]
        # Check file extension of the document if it matches a file extension of an image
        if not all(["." in document.filename, document.filename.rsplit(".", 1)[1].lower() in IMAGE_FORMAT_ALLOWED_EXTENSIONS]):
            abort(415)

        token: TokenDTO
        try:
            token = Register(self.user_repository,
                             self.token_repository,
                             self.license_repository).worker(CredentialDTO.json_to_self(credential),
                                                             account_status,
                                                             document.stream)
        except AccountAlreadyExist:
            abort(409)
        except LengthNameTooLong:
            abort(400)
        except Exception:
            abort(500)
        return jsonify(token.to_json())
