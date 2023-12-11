from flask import Blueprint, Response, jsonify, abort, request

from api.exceptions import InvalidValidationStatus, LicenseNotFound
from api.worker.auth.use_case import CheckToken
from api.worker.admin import DocumentType
from api.worker.admin.use_case import (
    GetLicenseToValidate,
    GetLicensesToValidate,
    IsUserAdmin,
    ValidateLicense
)
from database.exceptions import NotFound, DocumentAlreadyChecked
from database.repositories import (
    UserAdminRepositoryInterface,
    UserBannedRepositoryInterface,
    UserRepositoryInterface,
    LicenseRepositoryInterface, 
    TokenRepositoryInterface
)


class AdminRoutes(Blueprint):
    user_repository: UserRepositoryInterface
    user_admin_repository: UserAdminRepositoryInterface
    user_banned_repository: UserBannedRepositoryInterface
    license_repository: LicenseRepositoryInterface
    token_repository: TokenRepositoryInterface

    def __init__(self,
                 user_repository: UserRepositoryInterface,
                 user_admin_repository: UserAdminRepositoryInterface,
                 user_banned_repository: UserBannedRepositoryInterface,
                 token_repository: TokenRepositoryInterface,
                 license_repository: LicenseRepositoryInterface):
        super(AdminRoutes, self).__init__("admin", __name__, 
                                          url_prefix="/admin")
        
        self.token_repository = token_repository
        self.user_repository = user_repository
        self.user_admin_repository = user_admin_repository
        self.user_banned_repository = user_banned_repository
        self.license_repository = license_repository

        self.before_request(self.check_is_admin)
        self.route("/license/to-validate", 
                   methods=["GET"])(self.license_to_validate_api)
        self.route("/license", 
                   methods=["GET"])(self.get_license_api)
        self.route("/license/validate", 
                   methods=["POST"])(self.validate_license_api)

    def check_is_admin(self):
        authorization = request.headers.get("Authorization")
        if not authorization:
            abort(401)

        authorization_value = authorization.split(" ")
        if len(authorization_value) != 2 or authorization_value[0].lower() != "bearer":
            abort(401)

        is_token_valid: bool
        try:
            is_token_valid = CheckToken(self.token_repository,
                                        self.user_banned_repository,
                                        self.user_admin_repository).worker(authorization_value[1])
        except Exception:
            abort(500)

        if not is_token_valid:
            abort(401)

        if not IsUserAdmin(self.token_repository, self.user_admin_repository).worker(authorization_value[1]):
            abort(403)

    def license_to_validate_api(self) -> Response:
        query_data = request.args.to_dict()

        page: int | None = None
        try:
            page = int(query_data["page"])
        except Exception:
            pass

        try:
            licenses_to_validate = GetLicensesToValidate(self.license_repository).worker(page)
        except ValueError:
            abort(400)
        except Exception as e:
            abort(500)
        return jsonify(licenses_to_validate)

    def get_license_api(self):
        query_data = request.args.to_dict()

        document_id: int | None = None
        try:
            document_id = int(query_data["document_id"])
        except Exception:
            pass

        try:
            licenses_to_validate = GetLicenseToValidate(self.license_repository).worker(document_id)
        except ValueError:
            abort(400)
        except NotFound:
            abort(404)
        except DocumentAlreadyChecked:
            abort(410)
        except Exception:
            abort(500)
        return jsonify(licenses_to_validate.to_json())

    def validate_license_api(self) -> Response:
        if not request.is_json:
            abort(415)

        validation_information = request.json
        validation_information_args = validation_information.keys()
        if "statut" not in validation_information_args:
            abort(400)

        query_data = request.args.to_dict()

        license_id: int
        try:
            license_id = int(query_data["license_id"])
        except Exception:
            abort(400)

        next_document_id: int | None
        try:
            next_document_id = ValidateLicense(self.license_repository, self.user_repository).worker(license_id,
                                                                                                     validation_information["statut"])
        except LicenseNotFound:
            abort(404)
        except InvalidValidationStatus:
            abort(400)
        except Exception:
            abort(500)

        if not next_document_id:
            return '', 204
        return jsonify({
            "next_document_id": next_document_id,
        })
