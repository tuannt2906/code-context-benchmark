class FrostlineError(Exception):
    """Base error for the application."""

    status = 500


class ValidationError(FrostlineError):
    status = 422


class NotFound(FrostlineError):
    status = 404


class RegistryError(FrostlineError):
    status = 500
