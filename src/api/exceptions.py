import logging


class LoggedException(Exception):
    def __init__(self, message):
        super().__init__(message)
        logging.exception(message)


class AuthenticationException(LoggedException):
    def __init__(self, message: str):
        super().__init__(message)


class CredentialInvalid(AuthenticationException):
    def __init__(self, message="Invalid credentials"):
        super().__init__(message)


class AccountAlreadyExist(AuthenticationException):
    def __init__(self, message: str):
        super().__init__(message)


class ProfileAlreadyExist(LoggedException):
    def __init__(self, message="Profile already exist"):
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


class UserNotFound(LoggedException):
    def __init__(self, message="user not found"):
        super().__init__(message)


class DriverNotFound(LoggedException):
    def __init__(self, message="driver not found"):
        super().__init__(message)


class PassengerNotFound(LoggedException):
    def __init__(self, message="passenger not found"):
        super().__init__(message)


class InvalidValidationStatus(LoggedException):
    def __init__(self, message):
        super().__init__(message)


class InternalServerError(LoggedException):
    def __init__(self, message: str):
        super().__init__(message)


class CarpoolingAlreadyBooked(Exception):
    def __init__(self, message="carpooling already booked"):
        super().__init__(message)


class CarpoolingNotFound(Exception):
    def __init__(self, message="carpooling not found"):
        super().__init__(message)


class CarpoolingCanceled(Exception):
    def __init__(self, message="carpooling canceled"):
        super().__init__(message)


class CarpoolingAlreadyFull(Exception):
    def __init__(self, message="carpooling already full"):
        super().__init__(message)


class CarpoolingBookedTooLate(Exception):
    def __init__(self, message="departure time of carpooling is already passed"):
        super().__init__(message)


class CarpoolingReviewTimeExpired(Exception):
    def __init__(self,
                 message="The user can't review this carpooling, more than a week has passed since the trip was made"):
        self.message = message
        super().__init__(self.message)


class ScheduledCarpoolingCannotBeCreated(Exception):
    def __init__(self, message="scheduled carpooling cannot be crated due to conflicts"):
        super().__init__(message)
