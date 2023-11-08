from api import log


class DatabaseError(Exception):
    pass


class NotFound(DatabaseError):
    pass


class InternalServer(DatabaseError):
    pass


class UniqueViolation(DatabaseError):
    pass


class CredentialInvalid(Exception):
    def __init__(self, message="Invalid credentials"):
        super().__init__(message)
        log(f"CredentialInvalid exception: {str(self)}")

class BannedAccount(Exception):
    pass
