from hashlib import sha512

IMAGE_FORMAT_ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png"]


def hash(token: str) -> bytes:
    return sha512(token).digest


def log(msg: str):
    print(msg)
