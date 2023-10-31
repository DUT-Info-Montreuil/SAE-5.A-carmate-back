from flask import Flask


class Api(object):
    """
    All property about the API
    """
    api = Flask(__name__)
    port = 5000
    host = '0.0.0.0'

    def __init__(self) -> None:
        # add routes
        # self.api.register_blueprint()
        pass

    def run(self) -> None:
        self.api.run(port=self.port, host=self.host)


Api().run()
