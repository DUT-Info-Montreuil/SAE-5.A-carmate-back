from flask import Blueprint

from database import establishing_connection


class MonitoringRoutes(Blueprint):
    def __init__(self):
        super().__init__("monitoring", __name__,
                         url_prefix="/monitoring")
        
        self.route("/liveness",
                   methods=["GET"])(self.liveness_api)
        self.route("/readiness",
                   methods=["GET"])(self.readiness_api)

    def liveness_api(self):
        return '', 204
