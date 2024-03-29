from typing import Any

from flask import Blueprint, abort, request

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

    def readiness_api(self) -> None:
        if request.endpoint == "monitoring.liveness_api":
            return None

        try:
            conn = establishing_connection()
        except Exception:
            abort(503)
        rowcount: int
        with conn.cursor() as curs:
            curs.execute("SELECT 1;")
            rowcount = curs.rowcount
        conn.close()
        
        if rowcount != 1:
            abort(503)
