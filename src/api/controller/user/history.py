from flask import Blueprint, abort

from api.controller import token_is_valid, extract_token
from api.worker.user.use_case import GetHistory
from api.exceptions import UserNotFound


class HistoryRoutes(Blueprint):
    def __init__(self):
        super().__init__("history", __name__,
                         url_prefix="/user")

        self.before_request(token_is_valid)
        self.route("/history",
                   methods=["GET"])(self.history_api)

    def history_api(self):
        try:
            return GetHistory().worker(extract_token())
        except UserNotFound:
            abort(404)
        except Exception:
            abort(500)
