from flask import Blueprint, abort, jsonify, request

from api.controller import extract_token
from api.exceptions import UserNotFound
from api.worker.auth.models import UserInformationDTO
from api.worker.auth.use_case import CheckToken
from api.worker.user.models import UserDTO
from api.worker.user.use_case import GetUser


class UserRoutes(Blueprint):
    def __init__(self) -> None:
        super().__init__("user", __name__)

        self.before_request(self.check_token)
        self.route("/user",
                   methods=["GET"])(self.get_user_api)
        
    def check_token(self):
        token = extract_token()
        user_information: UserInformationDTO | None
        try:
            user_information = CheckToken().worker(token)
        except Exception:
            abort(500)

        if not user_information:
            abort(401)
        
        if "user_id" in request.args.keys():
            if not user_information.admin:
                abort(401)

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
                user = GetUser().worker(user_id=user_id)
            except UserNotFound:
                abort(404)
            except Exception:
                abort(500)
        elif "Authorization" in request.headers.keys():
            try:
                user = GetUser().worker(token=extract_token())
            except UserNotFound:
                abort(404)
            except Exception:
                abort(500)
        
        if not user:
            abort(400)
        return jsonify(user.to_json())
