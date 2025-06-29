"""Core exceptions for PyBastion."""


class PyBastionError(Exception):
    """Base exception for network scanner errors."""

    def __init__(self, message: str, details: dict[str, str] | None = None) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(PyBastionError):
    """Configuration-related errors."""


class ParsingError(PyBastionError):
    """Device configuration parsing errors."""

    def __init__(
        self,
        message: str,
        device_type: str | None = None,
        line_number: int | None = None,
        details: dict[str, str] | None = None,
    ) -> None:
        """Initialize the parsing error."""
        super().__init__(message, details)
        self.device_type = device_type
        self.line_number = line_number


class DatabaseError(PyBastionError):
    """Database operation errors."""


class ValidationError(PyBastionError):
    """Data validation errors."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: str | None = None,
        details: dict[str, str] | None = None,
    ) -> None:
        """Initialize the validation error."""
        super().__init__(message, details)
        self.field = field
        self.value = value


class AnalysisError(PyBastionError):
    """Security analysis errors."""


class ReportError(PyBastionError):
    """Report generation errors."""


class UnsupportedDeviceError(PyBastionError):
    """Unsupported device type errors."""

    def __init__(
        self,
        device_type: str,
        supported_types: list[str] | None = None,
    ) -> None:
        """Initialize the unsupported device error."""
        message = f"Unsupported device type: {device_type}"
        if supported_types:
            message += f". Supported types: {', '.join(supported_types)}"
        super().__init__(message)
        self.device_type = device_type
        self.supported_types = supported_types or []


class APIError(PyBastionError):
    """External API errors."""

    def __init__(
        self,
        message: str,
        api_name: str | None = None,
        status_code: int | None = None,
        details: dict[str, str] | None = None,
    ) -> None:
        """Initialize the API error."""
        super().__init__(message, details)
        self.api_name = api_name
        self.status_code = status_code


# Aliases for backward compatibility
NetworkScannerError = PyBastionError
NetworkSecurityScannerError = PyBastionError
ParserError = ParsingError
NormalizationError = ValidationError
APIClientError = APIError
ReportGenerationError = ReportError
