import logging


class DatabaseError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NotFound(DatabaseError):
    def __init__(self, message: str):
        super().__init__(message)


class InternalServer(DatabaseError):
    def __init__(self, message: str):
        super().__init__(message)


class UniqueViolation(DatabaseError):
    def __init__(self, message: str):
        super().__init__(message)


class CredentialInvalid(Exception):
    def __init__(self, message="Invalid credentials"):
        super().__init__(message)
        logging.exception(f"CredentialInvalid exception: {str(self)}")


class BannedAccount(Exception):
    pass
