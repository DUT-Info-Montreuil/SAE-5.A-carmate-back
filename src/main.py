from flask import Flask

from api.controller.monitoring import monitoring


class Api(object):
    """
    All property about the API
    """
    api = Flask(__name__)
    port = 5000
    host = '0.0.0.0'

    def __init__(self) -> None:
        self.api.register_blueprint(monitoring)

    def run(self) -> None:
        self.api.run(port=self.port, host=self.host)


if __name__ == "__main__":
    Api().run()
