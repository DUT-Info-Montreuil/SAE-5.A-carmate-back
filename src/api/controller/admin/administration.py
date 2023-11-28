import os

from flask import Blueprint, Response, jsonify, abort, request

from api.worker.admin.use_case.get_license_to_validate import GetLicenseToValidate
from api.worker.admin.use_case.is_user_admin import IsUserAdmin
from api.worker.auth.use_case.check_token import CheckToken
from database.exceptions import NotFound, DocumentAlreadyChecked
from database.repositories import LicenseRepositoryInterface, LicenseRepository, TokenRepositoryInterface, \
    TokenRepository
from database.repositories.user_admin_repository import UserAdminRepositoryInterface, UserAdminRepository
from api.worker.admin.use_case.get_licenses_to_validate import GetLicensesToValidate
from test.mock import InMemoryLicenseRepository, InMemoryTokenRepository
from test.mock.admin import InMemoryUserAdminRepository

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
                token_repository = InMemoryTokenRepository()
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
    except Exception:
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
