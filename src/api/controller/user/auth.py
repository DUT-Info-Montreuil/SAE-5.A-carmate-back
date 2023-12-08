from flask import Blueprint, abort, jsonify, request, Response

from api import IMAGE_FORMAT_ALLOWED_EXTENSIONS
from api.worker.user import AccountStatus
from api.worker.auth.models import TokenDTO, CredentialDTO
from api.exceptions import AccountAlreadyExist, BannedAccount, CredentialInvalid, LengthNameTooLong
from api.worker.auth.use_case import Register, Login, CheckToken
from database.repositories import (
    TokenRepositoryInterface,
    UserRepositoryInterface,
    LicenseRepositoryInterface
)


class AuthRoutes(Blueprint):
    user_repository: UserRepositoryInterface
    token_repository: TokenRepositoryInterface
    license_repository: LicenseRepositoryInterface

    def __init__(self,
                 user_repository: UserRepositoryInterface,
                 token_repository: TokenRepositoryInterface,
                 license_repository: LicenseRepositoryInterface):
        super().__init__("auth", __name__,
                         url_prefix="/auth")

        self.token_repository = token_repository
        self.user_repository = user_repository
        self.license_repository = license_repository

        self.route("/check-token",
                   methods=["POST"])(self.check_token_api)
        self.route("/login",
                   methods=["POST"])(self.login_api)
        self.route("/register",
                   methods=["POST"])(self.register_api)

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

        token_is_valid: bool
        try:
            token_is_valid = CheckToken(self.token_repository).worker(token)
        except Exception:
            abort(500)

        if token_is_valid:
            return '', 204
        return '', 401

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
        if request.is_json:
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
