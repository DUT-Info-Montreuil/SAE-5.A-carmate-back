import logging


class LoggedException(Exception):
    def __init__(self, message):
        super().__init__(message)
        logging.exception(message)
