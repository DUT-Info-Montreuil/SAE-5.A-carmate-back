import re

from hashlib import sha512

from .exceptions import EmailFormatInvalid

IMAGE_FORMAT_ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
EMAIL_FORMAT_REGEX = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'


def hash(token: str) -> bytes:
    return sha512(token.encode()).digest()


def check_email(email: str) -> None:
    if not re.match(EMAIL_FORMAT_REGEX, email):
        raise EmailFormatInvalid()
