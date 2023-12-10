from flask import Blueprint, abort, jsonify, request, Response
#from flasgger import swag_from

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
        """
        Endpoint to check the validity of a user token.

        This endpoint validates a user token and returns user information if valid.

        ---
        parameters:
          - name: token
            in: body
            required: true
            type: string
            description: The user authentication token.
        responses:
          200:
            description: User information in JSON format.
          401:
            description: Unauthorized. Invalid token.
          415:
            description: Unsupported Media Type. Request must be in JSON format.
          500:
            description: Internal Server Error.
        """
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
                                   self.user_admin_repository).worker(token)
        except Exception:
            abort(500)

        if not user_info:
            return '', 401
        return jsonify(user_info.to_json())

    def login_api(self) -> Response:
        """
        Endpoint for user login.

        This endpoint handles user authentication by verifying the provided credentials.

        ---
        parameters:
          - name: email_address
            in: body
            required: true
            type: string
            description: The email address of the user.
          - name: password
            in: body
            required: true
            type: string
            description: The password of the user.
        responses:
          200:
            description: Authentication successful. Returns user token.
          401:
            description: Unauthorized. Invalid credentials.
          403:
            description: Forbidden. Banned account.
          415:
            description: Unsupported Media Type. Request must be in JSON format.
          500:
            description: Internal Server Error.
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
        """
        Endpoint for user registration.

        This endpoint registers a new user and returns a session token.

        ---
        parameters:
          - name: first_name
            in: formData
            required: true
            type: string
            description: The first name of the user.
          - name: last_name
            in: formData
            required: true
            type: string
            description: The last name of the user.
          - name: email_address
            in: formData
            required: true
            type: string
            description: The email address of the user.
          - name: password
            in: formData
            required: true
            type: string
            description: The password of the user.
          - name: type
            in: formData
            required: true
            type: string
            description: The type of account (e.g., "passenger").
          - name: document
            in: formData
            required: true
            type: file
            description: The user document (image file).
        responses:
          200:
            description: Registration successful. Returns user token.
          400:
            description: Bad Request. Invalid input or missing values.
          409:
            description: Conflict. User already exists.
          415:
            description: Unsupported Media Type. Invalid document format.
          500:
            description: Internal Server Error.
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
