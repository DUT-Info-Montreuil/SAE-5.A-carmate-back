from typing import List
from flask import (
    Blueprint,
    abort,
    jsonify
)

from api.controller import token_is_valid, extract_token
from api.worker.auth.models import UserInformationDTO
from api.worker.auth.use_case import CheckToken
from api.worker.user.models import (
    PublishedCarpoolingDTO,
    BookedCarpoolingDTO,
    PublishedScheduleCarpoolingDTO
)
from api.worker.user.use_case import (
    GetPublishedCarpooling,
    GetBookedCarpoolings,
    GetPublishedScheduleCarpooling
)


class HistoryRoutes(Blueprint):
    def __init__(self):
        super().__init__("history", __name__,
                         url_prefix="/history")

        self.before_request(token_is_valid)
        self.route("/carpooling/booked",
                   methods=["GET"])(self.history_carpooling_booked_api)
        self.route("/carpooling/published",
                   methods=["GET"])(self.history_carpooling_published_api)
        self.route("/schedule-carpooling/published",
                   methods=["GET"])(self.history_schedule_carpooling_published_api)

    def history_carpooling_booked_api(self):
        booked_carpoolings: List[BookedCarpoolingDTO]
        try:
            booked_carpoolings = GetBookedCarpoolings().worker(extract_token())
        except Exception:
            abort(500)
        return jsonify([booked_carpooling.to_json() for booked_carpooling in booked_carpoolings])        

    def history_carpooling_published_api(self):
        token = extract_token()

        user_information: UserInformationDTO
        try:
            user_information = CheckToken().worker(token)
        except Exception:
            abort(500)
        
        if not user_information.driver:
            abort(403)

        published_carpoolings: List[PublishedCarpoolingDTO]
        try:
            published_carpoolings = GetPublishedCarpooling().worker(token)
        except Exception:
            abort(500)
        return jsonify([published_carpooling.to_json() for published_carpooling in published_carpoolings])
    
    def history_schedule_carpooling_published_api(self):
        token = extract_token()

        user_information: UserInformationDTO
        try:
            user_information = CheckToken().worker(token)
        except Exception:
            abort(500)
        
        if not user_information.driver:
            abort(403)

        published_schedule_carpoolings: List[PublishedScheduleCarpoolingDTO]
        try:
            published_schedule_carpoolings = GetPublishedScheduleCarpooling().worker(token)
        except Exception:
            abort(500)
        return jsonify([PublishedScheduleCarpoolingDTO(*published_schedule_carpooling) for published_schedule_carpooling in published_schedule_carpoolings])