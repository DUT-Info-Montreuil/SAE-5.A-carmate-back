class AuthenticationException(Exception):
    pass


class AccountAlreadyExist(AuthenticationException):
    pass


class LengthNameTooLong(AuthenticationException):
    pass


class EmailFormatInvalid(AuthenticationException):
    pass


class InternalServerError(AuthenticationException):
    pass
