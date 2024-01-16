from typing import List
from flask import (
    Blueprint,
    abort,
    request,
    jsonify
)

from api.worker.user.models import PublishedCarpoolingDTO
from api.worker.user.use_case import GetPublishedCarpooling


class PublishedCarpoolingRoutes(Blueprint):
    def __init__(self):
        super().__init__("published_carpooling", __name__,
                         url_prefix="/driver/carpooling")
        
        self.route("/published",
                   methods=["GET"])(self.user_published_carpooling_api)

    def user_published_carpooling_api(self):
        if not "driver_id" in request.args:
            abort(400)

        published_carpoolings: List[PublishedCarpoolingDTO] = []
        try:
            published_carpoolings = GetPublishedCarpooling().worker(request.args["driver_id"])
        except Exception:
            abort(500)
        return jsonify([published_carpooling.to_json() for published_carpooling in published_carpoolings])

