import logging
import os

from waitress import serve
from flask import (
    Flask,
    Response,
    request
)

from api.controller import *


class Api:
    """
    All property about the API
    """
    host = '0.0.0.0'

    logging_level = logging.DEBUG
    logging_format = '[%(levelname)s][%(asctime)s] %(message)s'

    def __init__(self) -> None:
        self.api = Flask("carmate-api" if not os.getenv("API_NAME") else os.getenv("API_NAME"))

        logging.basicConfig(format=self.logging_format,
                            datefmt='%d/%m/%Y %I:%M:%S %p',
                            level=self.logging_level)

        monitoring = MonitoringRoutes()
        auth = AuthRoutes()
        profiles = ProfilesRoutes()
        self.api.register_blueprint(monitoring)
        self.api.register_blueprint(AdminRoutes())
        self.api.register_blueprint(profiles)
        self.api.register_blueprint(auth)
        self.api.register_blueprint(UserRoutes())
        self.api.register_blueprint(SearchRoutes())
        self.api.register_blueprint(CarpoolingWithDriverCheckRoutes())
        self.api.register_blueprint(BookingRoutes())
        self.api.register_blueprint(ReviewRoutes())
        self.api.register_blueprint(ScheduleCarpoolingRoutes())
        self.api.register_blueprint(ConfirmRoutes())
        self.api.register_blueprint(ScoreboardRoutes())
        self.api.register_blueprint(PublishedCarpoolingRoutes())

        if os.getenv("API_MODE") == "PROD":
            self.api.after_request(self.handle_preflight_requests)
            self.api.before_request(monitoring.readiness_api)

    def handle_preflight_requests(self, response: Response):
        if request.method == 'OPTIONS':
            response.status_code = 200
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'content-type,authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, HEAD')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Content-Type', 'application/json')
        return response

    def run(self) -> None:
        if not os.getenv("API_PORT"):
            raise Exception("API_PORT must be set !")
        self.port = int(os.getenv("API_PORT"))

        match os.getenv("API_MODE"):
            case "PROD":
                serve(self.api,
                      host=self.host,
                      port=self.port)
            case "TEST":
                self.api.run(port=self.port,
                             host=self.host)
            case _:
                error_msg = f"Value {os.getenv('API_MODE')} in API_MODE is invalid !"
                logging.exception(error_msg)
                raise Exception(error_msg)


Api().run()
