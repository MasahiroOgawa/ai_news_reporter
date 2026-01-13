"""Custom exceptions for AI News Reporter."""


class AINewsReporterError(Exception):
    """Base exception for AI News Reporter."""

    pass


class ConfigurationError(AINewsReporterError):
    """Configuration related errors."""

    pass


class CollectorError(AINewsReporterError):
    """Data collection related errors."""

    pass


class LLMError(AINewsReporterError):
    """LLM processing related errors."""

    pass


class DeliveryError(AINewsReporterError):
    """Report delivery related errors."""

    pass
