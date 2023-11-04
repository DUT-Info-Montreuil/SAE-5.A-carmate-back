from hashlib import sha512


def hash(token: str) -> bytes:
    sha512(token).digest


def log(msg: str):
    print(msg)
