from flask import Blueprint, abort, jsonify, request

from api.exceptions import CredentialInvalid, UserNotFound
from api.worker.auth.models import UserInformationDTO
from api.worker.auth.use_case import CheckToken
from api.worker.user.models import UserDTO
from api.worker.user.use_case import GetUser
from database.repositories import (
    TokenRepositoryInterface,
    UserRepositoryInterface,
    UserBannedRepositoryInterface,
    UserAdminRepositoryInterface,
    LicenseRepositoryInterface
)


class UserRoutes(Blueprint):
    user_repository: UserRepositoryInterface
    token_repository: TokenRepositoryInterface
    user_banned_repository: UserBannedRepositoryInterface
    user_admin_repository: UserAdminRepositoryInterface
    license_repository: LicenseRepositoryInterface

    def __init__(self,
                 user_repository: UserRepositoryInterface,
                 token_repository: TokenRepositoryInterface,
                 user_banned_repository: UserBannedRepositoryInterface,
                 user_admin_repository: UserAdminRepositoryInterface,
                 license_repository: LicenseRepositoryInterface) -> None:
        super().__init__("user", __name__)
        
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.user_banned_repository = user_banned_repository
        self.user_admin_repository = user_admin_repository
        self.license_repository = license_repository

        self.before_request(self.check_token)
        self.route("/user",
                   methods=["GET"])(self.get_user_api)
        
    def check_token(self):
        authorization = request.headers.get("Authorization")
        if not authorization:
            abort(401)

        authorization_value = authorization.split(" ")
        if len(authorization_value) != 2 or authorization_value[0].lower() != "bearer":
            abort(401)

        user_information: UserInformationDTO | None
        try:
            user_information = CheckToken(self.token_repository,
                                          self.user_banned_repository,
                                          self.user_admin_repository,
                                          self.license_repository).worker(authorization_value[1])
        except Exception:
            abort(500)

        if not user_information:
            abort(401)
        
        if "user_id" in request.args.keys():
            if not user_information.admin:
                abort(401)

    def extract_token(self, authorization: str):
        if not authorization:
            raise CredentialInvalid()

        authorization_value = authorization.split(" ")
        if len(authorization_value) != 2 or authorization_value[0].lower() != "bearer":
            raise CredentialInvalid()
        return authorization_value[1]

    def get_user_api(self):
        user: UserDTO | None = None
        if "user_id" in request.args.keys():
            user_id: int
            try:
                user_id = int(request.args.get("user_id"))
            except ValueError:
                abort(400)
            except Exception:
                abort(500)

            try:
                user = GetUser(self.user_repository,
                               self.token_repository).worker(user_id=user_id)
            except UserNotFound:
                abort(404)
            except Exception:
                abort(500)
        elif "Authorization" in request.headers.keys():
            try:
                user = GetUser(self.user_repository,
                               self.token_repository).worker(token=self.extract_token(request.headers.get("Authorization")))
            except UserNotFound:
                abort(404)
            except Exception:
                abort(500)
        
        if not user:
            abort(400)
        return jsonify(user.to_json())
