from flask import Blueprint, Response, jsonify, abort, request

from api.controller import extract_token
from api.worker.auth.use_case import CheckToken
from api.worker.auth.models import UserInformationDTO
from api.worker.admin.use_case import (
    GetLicenseToValidate,
    GetLicensesToValidate,
    IsUserAdmin,
    ValidateLicense
)
from api.exceptions import InvalidValidationStatus, LicenseNotFound
from database.exceptions import NotFound, DocumentAlreadyChecked


class AdminRoutes(Blueprint):
    def __init__(self):
        super(AdminRoutes, self).__init__("admin", __name__,
                                          url_prefix="/admin")

        self.before_request(self.check_is_admin)
        self.route("/license/to-validate",
                   methods=["GET"])(self.license_to_validate_api)
        self.route("/license",
                   methods=["GET"])(self.get_license_api)
        self.route("/license/validate",
                   methods=["POST"])(self.validate_license_api)

    def check_is_admin(self) -> None:
        """Check thanks to the session token in the headers, if the user is an admin
        
        :raises:
            - 401: don't have Authorization header, schema invalid or token invalid
            - 403: Is not admin
            - 500: InternalServerError (other)
        """
        token = extract_token()
        user_info_dto: UserInformationDTO
        try:
            user_info_dto = CheckToken().worker(token)
        except Exception:
            abort(500)

        if not user_info_dto:
            abort(401)

        if not IsUserAdmin().worker(token):
            abort(403)

    def license_to_validate_api(self) -> Response:
        """List licenses with state 'Pending'
        
        :raises:
            - 400: if the value of page argument request is not valid
            - 401: don't have Authorization header, schema invalid or token invalid
            - 403: Is not admin
            - 500: InternalServerError (other)
        Return: A json with licenses to validate
        """
        query_data = request.args.to_dict()

        page: int | None = None
        try:
            page = int(query_data["page"])
        except Exception:
            pass

        try:
            licenses_to_validate = GetLicensesToValidate().worker(page)
        except ValueError:
            abort(400)
        except Exception as e:
            abort(500)
        return jsonify(licenses_to_validate)

    def get_license_api(self):
        """Get one document which must be validated
        
        :raises:
            - 400: If document_id value is not an integer or document_id is not an attribute
            - 401: don't have Authorization header, schema invalid or token invalid
            - 403: Is not admin
            - 404: License not found
            - 410: Document already approved or rejected
            - 500: InternalServerError (other)
        Return: return_description
        """
        query_data = request.args.to_dict()

        document_id: int | None = None
        try:
            document_id = int(query_data["document_id"])
        except ValueError:
            abort(400)
        except Exception:
            pass

        try:
            licenses_to_validate = GetLicenseToValidate().worker(document_id)
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
        """Rejected or approved a license
        
        :raises:
            - 400: Status, license_id or validation status invalid is not present in the json data
            - 401: don't have Authorization header, schema invalid or token invalid
            - 403: Is not admin
            - 415: Content type is not application/json
            - 500: InternalServerError (other)
        Return: nothing or the next document_id
        """

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
            next_document_id = ValidateLicense().worker(license_id,
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
