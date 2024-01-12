import secrets

from abc import ABC


class PassengerCodeServiceInterface(ABC):
    @staticmethod
    def next() -> int: ...


class PassengerCodeService(PassengerCodeServiceInterface):
    @staticmethod
    def next() -> int:
        return int(''.join([str(secrets.randbelow(10)) for n in range(6)]))
