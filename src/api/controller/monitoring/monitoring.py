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
        if request.endpoint in "liveness" or request.endpoint in "readiness":
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

        if request.method == "GET":
            return '', 204
