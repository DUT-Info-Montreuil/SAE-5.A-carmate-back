class DatabaseError(Exception):
    pass


class NotFound(DatabaseError):
    pass


class InternalServer(DatabaseError):
    pass


class UniqueViolation(DatabaseError):
    pass
