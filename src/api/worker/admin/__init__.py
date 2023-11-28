from enum import Enum, auto


class ValidationStatus(Enum):
    Pending = auto()
    Approved = auto()
    Rejected = auto()


class DocumentType(Enum):
    Driver = auto()
    Basic = auto()
