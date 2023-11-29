from flask import Blueprint


monitoring = Blueprint("monitoring", __name__,
                       url_prefix="/monitoring")


@monitoring.route("/readiness")
def readiness_api():
    return '', 204
