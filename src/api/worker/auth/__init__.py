import secrets
import string


class Token:
    LENGTH: int = 128

    @staticmethod
    def generate() -> str:
        return ''.join(secrets.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(Token.LENGTH))
