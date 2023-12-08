from abc import ABC


class TokenInterface(ABC):
    @staticmethod
    def generate() -> str: ...
