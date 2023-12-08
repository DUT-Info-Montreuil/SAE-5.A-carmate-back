import secrets
import string

from api.worker.auth.interfaces import TokenInterface


class Token(TokenInterface):
    LENGTH: int = 128

    @staticmethod
    def generate() -> str:
        return ''.join(secrets.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(Token.LENGTH))
