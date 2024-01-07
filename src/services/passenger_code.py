from abc import ABC


class PassengerCodeServiceInterface(ABC):
    @staticmethod
    def next() -> int: ...


class PassengerCodeService(PassengerCodeServiceInterface):
    @staticmethod
    def next() -> int:
        return 123456
