import os

from flask import Blueprint, abort, jsonify, request, Response

from api import IMAGE_FORMAT_ALLOWED_EXTENSIONS
from api.worker.user import AccountStatus
from api.worker.auth.models import TokenDTO, CredentialDTO
from api.worker.auth.use_case.login import Login
from api.worker.auth.exceptions import AccountAlreadyExist, BannedAccount, CredentialInvalid, LengthNameTooLong
from api.worker.auth.use_case.register import Register
from database.repositories import UserRepository, TokenRepository, TokenRepositoryInterface, UserRepositoryInterface
from database.repositories.license_repository import LicenseRepository, LicenseRepositoryInterface
from test.mock import InMemoryTokenRepository, InMemoryUserRepository
from test.mock.user.in_memory_license_repository import InMemoryLicenseRepository

auth = Blueprint("auth", __name__,
                 url_prefix="/auth")


@auth.route("/login", methods=["POST"])
def login_api() -> Response:
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
    user_repository: UserRepositoryInterface
    token_repository: TokenRepositoryInterface
    try:
        api_mode = os.getenv("API_MODE")
        match api_mode:
            case "PROD":
                user_repository = UserRepository
                token_repository = TokenRepository
            case "TEST":
                user_repository = InMemoryUserRepository
                token_repository = InMemoryTokenRepository

        token = Login(user_repository, token_repository).worker(CredentialDTO.json_to_self(credential))
    except CredentialInvalid:
        abort(401)
    except BannedAccount:
        abort(403)
    except Exception:
        abort(500)
    return jsonify(token.to_json())


@auth.route("/register", methods=["POST"])
def register_api() -> Response:
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
    user_repository: UserRepositoryInterface
    token_repository: TokenRepositoryInterface
    license_repository: LicenseRepositoryInterface
    try:
        match os.getenv("API_MODE"):
            case "PROD":
                user_repository = UserRepository
                token_repository = TokenRepository
                license_repository = LicenseRepository
            case "TEST":
                user_repository = InMemoryUserRepository
                token_repository = InMemoryTokenRepository
                license_repository = InMemoryLicenseRepository

        token = Register(user_repository,
                         token_repository,
                         license_repository).worker(CredentialDTO.json_to_self(credential),
                                                    account_status,
                                                    document.stream)
    except AccountAlreadyExist:
        abort(409)
    except LengthNameTooLong:
        abort(400)
    except Exception:
        abort(500)
    return jsonify(token.to_json())