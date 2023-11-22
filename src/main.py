import logging

from flask import Flask

from api.controller.user import auth


class Api(object):
    """
    All property about the API
    """
    logging_level = logging.DEBUG
    logging_format = '[%(levelname)s][%(asctime)s] %(message)s'

    api = Flask("carmate-api")
    port = 5000
    host = '0.0.0.0'

    def __init__(self) -> None:
        logging.basicConfig(format=self.logging_format,
                            datefmt='%d/%m/%Y %I:%M:%S %p',
                            level=self.logging_level)

        self.api.register_blueprint(auth)

    def run(self) -> None:
        self.api.run(port=self.port, 
                     host=self.host)


Api().run()
