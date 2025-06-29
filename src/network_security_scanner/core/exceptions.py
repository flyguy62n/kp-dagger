"""Core exceptions for the network security scanner."""


class NetworkScannerError(Exception):
    """Base exception for network scanner errors."""

    def __init__(self, message: str, details: dict[str, str] | None = None) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(NetworkScannerError):
    """Configuration-related errors."""

    pass


class ParsingError(NetworkScannerError):
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


class DatabaseError(NetworkScannerError):
    """Database operation errors."""

    pass


class ValidationError(NetworkScannerError):
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


class AnalysisError(NetworkScannerError):
    """Security analysis errors."""

    pass


class ReportError(NetworkScannerError):
    """Report generation errors."""

    pass


class UnsupportedDeviceError(NetworkScannerError):
    """Unsupported device type errors."""

    def __init__(
        self, device_type: str, supported_types: list[str] | None = None
    ) -> None:
        """Initialize the unsupported device error."""
        message = f"Unsupported device type: {device_type}"
        if supported_types:
            message += f". Supported types: {', '.join(supported_types)}"
        super().__init__(message)
        self.device_type = device_type
        self.supported_types = supported_types or []


class APIError(NetworkScannerError):
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
NetworkSecurityScannerError = NetworkScannerError
ParserError = ParsingError
NormalizationError = ValidationError
APIClientError = APIError
ReportGenerationError = ReportError
