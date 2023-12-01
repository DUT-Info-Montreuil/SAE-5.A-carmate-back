import os

from flask import Blueprint, Response, jsonify, abort, request
from api.worker.admin import DocumentType

from api.worker.admin.use_case.get_license_to_validate import GetLicenseToValidate
from api.worker.admin.use_case.get_licenses_to_validate import GetLicensesToValidate
from api.worker.admin.use_case.is_user_admin import IsUserAdmin
from api.worker.auth.exceptions import InvalidValidationStatus, LicenseNotFound
from api.worker.auth.use_case.check_token import CheckToken
from api.worker.admin.use_case import GetLicenseToValidate
from api.worker.admin.use_case import ValidateLicense
from database.exceptions import NotFound, DocumentAlreadyChecked
from database.repositories import LicenseRepositoryInterface, LicenseRepository, TokenRepositoryInterface, \
    TokenRepository
from database.repositories.user_admin_repository import UserAdminRepositoryInterface, UserAdminRepository
from database.repositories.user_repository import UserRepository, UserRepositoryInterface
from test.mock import InMemoryLicenseRepository, InMemoryTokenRepository
from test.mock.admin import InMemoryUserAdminRepository
from test.mock.user import InMemoryUserRepository

admin = Blueprint("admin", __name__,
                  url_prefix="/admin")


@admin.before_request
def check_is_admin():
    authorization = request.headers.get("Authorization")

    if authorization is None:
        abort(401)

    authorization_value = authorization.split(" ")
    if len(authorization_value) != 2 or authorization_value[0].lower() != "bearer":
        abort(401)

    token_repository: TokenRepositoryInterface
    user_admin_repository: UserAdminRepositoryInterface
    is_token_valid: bool
    try:
        match os.getenv("API_MODE"):
            case "PROD":
                token_repository = TokenRepository()
                user_admin_repository = UserAdminRepository()
            case "TEST":
                token_repository = InMemoryTokenRepository(InMemoryUserRepository())
                user_admin_repository = InMemoryUserAdminRepository()
            case _:
                raise Exception()

        is_token_valid = CheckToken(token_repository).worker(authorization_value[1])
    except Exception:
        abort(500)

    if not is_token_valid:
        abort(401)

    if not IsUserAdmin(token_repository, user_admin_repository).worker(authorization_value[1]):
        abort(403)


@admin.route("/license/to-validate", methods=["GET"])
def license_to_validate_api() -> Response:
    license_repository: LicenseRepositoryInterface
    page: int | None = None

    try:
        match os.getenv("API_MODE"):
            case "PROD":
                license_repository = LicenseRepository()
            case "TEST":
                license_repository = InMemoryLicenseRepository()
            case _:
                raise Exception()

        query_data = request.args.to_dict()

        try:
            page = int(query_data["page"])
        except Exception:
            pass

        licenses_to_validate = GetLicensesToValidate(license_repository).worker(page)

    except ValueError:
        abort(400)
    except Exception as e:
        abort(500)

    return jsonify(licenses_to_validate)


@admin.route("/license", methods=["GET"])
def get_license():
    license_repository: LicenseRepositoryInterface
    document_id: int | None = None

    try:
        match os.getenv("API_MODE"):
            case "PROD":
                license_repository = LicenseRepository()
            case "TEST":
                license_repository = InMemoryLicenseRepository()
            case _:
                raise Exception()

        query_data = request.args.to_dict()

        try:
            document_id = int(query_data["document_id"])
        except Exception:
            pass

        licenses_to_validate = GetLicenseToValidate(license_repository).worker(document_id)

    except ValueError:
        abort(400)
    except NotFound:
        abort(404)
    except DocumentAlreadyChecked:
        abort(410)
    except Exception:
        abort(500)

    return jsonify(licenses_to_validate.to_json())


@admin.route("/license/validate", methods=["POST"])
def valide_license_api():
    if not request.is_json:
        abort(415)

    validation_information = request.json
    validation_information_args = validation_information.keys()
    if any(["statut" not in validation_information_args, "document_type" not in validation_information_args, "email" not in validation_information_args]):
        abort(400)

    try:
        DocumentType[validation_information["document_type"]]
    except ValueError:
        abort(400)

    query_data = request.args.to_dict()

    license_id: int 
    try:
        license_id = int(query_data["license_id"])
    except Exception:
        abort(400)

    next_document: tuple | None
    license_repository: LicenseRepositoryInterface
    user_repository: UserRepositoryInterface
    try:
        match os.getenv("API_MODE"):
            case "PROD":
                license_repository = LicenseRepository()
                user_repository = UserRepository()
            case "TEST":
                license_repository = InMemoryLicenseRepository()
                user_repository = InMemoryUserRepository()

        next_document = ValidateLicense(license_repository, 
                                        user_repository).worker(license_id, 
                                                                validation_information["statut"])
    except LicenseNotFound:
        abort(404)
    except InvalidValidationStatus:
        abort(400)
    except Exception:
        abort(500)

    if not next_document:
        return '', 204
    return jsonify({"next_email": next_document[1].email_address, "next_document_type": next_document[0].document_type})
