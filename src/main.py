import logging
import os

from waitress import serve
from flask import Flask
from flask_cors import CORS

from api.controller.user import auth


class Api(object):
    """
    All property about the API
    """
    logging_level = logging.DEBUG
    logging_format = '[%(levelname)s][%(asctime)s] %(message)s'

    host = '0.0.0.0'

    def __init__(self) -> None:
        if not os.getenv("API_MODE"):
            raise Exception("API_MODE must be set !")

        logging.basicConfig(format=self.logging_format,
                            datefmt='%d/%m/%Y %I:%M:%S %p',
                            level=self.logging_level)

        self.api = Flask("carmate-api" if not os.getenv("API_NAME") else os.getenv("API_NAME"))
        self.cors = CORS(self.api, resources={r"*": {"origins": "*"}})

        self.api.register_blueprint(auth)

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
