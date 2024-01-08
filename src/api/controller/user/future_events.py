from flask import Blueprint, abort, jsonify

from api.controller import extract_token
from api.worker.auth.use_case import CheckToken
from api.worker.user.use_case.get_future_events import GetFutureEvents
from database.exceptions import NotFound


class FutureEventsRoutes(Blueprint):
    def __init__(self):
        super().__init__("future_events", __name__,
                         url_prefix="/future-events")

        self.route("/",
                   methods=["GET"])(self.get_future_events_api)

    def get_future_events_api(self):
        token = extract_token()
        user_infos = CheckToken().worker(token)

        if not user_infos:
            abort(401)
        if user_infos.banned:
            abort(403)

        try:
            future_events = GetFutureEvents().worker(token)
        except NotFound:
            abort(401)
        except Exception:
            abort(500)

        return jsonify(future_events.to_json())
