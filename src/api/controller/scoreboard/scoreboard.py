from flask import Blueprint, abort, jsonify

from api.worker.scoreboard.use_case import *


class ScoreboardRoutes(Blueprint):
    def __init__(self):
        super().__init__("scoreboard", __name__,
                         url_prefix="/scoreboard")
        
        self.route("/economic-driving",
                   methods=["GET"])(self.economic_driving_scoreboard_api)
        self.route("/safe-driving",
                   methods=["GET"])(self.safe_driving_scoreboard_api)
        self.route("/sociability",
                   methods=["GET"])(self.sociability_scoreboard_api)
        
    def economic_driving_scoreboard_api(self):
        try:
            return jsonify([score_dto.to_json() for score_dto in GetBestEconomicDrivingRating().worker()])
        except Exception:
            abort(500)

    def safe_driving_scoreboard_api(self):
        try:
            return jsonify([score_dto.to_json() for score_dto in GetBestSafeDrivingRating().worker()])
        except Exception:
            abort(500)

    def sociability_scoreboard_api(self):
        try:
            return jsonify([score_dto.to_json() for score_dto in GetBestSociabilityRating().worker()])
        except Exception:
            abort(500)
