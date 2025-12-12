"""Custom exceptions for the application."""


class ServiceError(Exception):
    """Base class for service exceptions."""
    pass


class OpenAIServiceError(ServiceError):
    """Exception raised when OpenAI service fails."""
    pass


class PDFServiceError(ServiceError):
    """Exception raised when PDF service fails."""
    pass
