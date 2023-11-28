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


class DocumentAlreadyChecked(Exception):
    def __init__(self, message: str):
        super().__init__(message)
