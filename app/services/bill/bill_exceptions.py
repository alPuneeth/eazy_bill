# Bill Domain Exceptions

class BillError(Exception):
    """Base exception for bill domain"""
    pass


class BillNotFoundError(BillError):
    """Raised when bill is not found"""
    pass


class BillConflictError(BillError):
    pass


class CustomerNotFoundError(BillError):
    pass


class InvalidPackageError(BillError):
    pass


class BillUpdateNotAllowedError(BillError):
    pass


class EmptyUpdateError(BillError):
    pass


class OverlappinBillingPeriod(BillError):
    pass


class VillageNotFoundError(BillError):
    pass