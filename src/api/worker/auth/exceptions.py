from api.worker import LoggedException


class AuthenticationException(LoggedException):
    def __init__(self, message: str):
        super().__init__(message)


class CredentialInvalid(AuthenticationException):
    def __init__(self, message="Invalid credentials"):
        super().__init__(message)


class AccountAlreadyExist(AuthenticationException):
    def __init__(self, message: str):
        super().__init__(message)


class BannedAccount(AuthenticationException):
    def __init__(self, message: str):
        super().__init__(message)


class LengthNameTooLong(AuthenticationException):
    def __init__(self, message: str):
        super().__init__(message)


class EmailFormatInvalid(AuthenticationException):
    def __init__(self, message="email format invalid"):
        super().__init__(message)


class LicenseNotFound(LoggedException):
    def __init__(self, message="license not found"):
        super().__init__(message)

class InvalidValidationStatus(LoggedException):
    def __init__(self, message):
        super().__init__(message)


class InternalServerError(AuthenticationException):
    def __init__(self, message: str):
        super().__init__(message)
