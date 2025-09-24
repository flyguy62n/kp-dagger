"""Core exceptions for Dagger."""


class DaggerError(Exception):
    """Base exception for network scanner errors."""

    def __init__(self, message: str, details: dict[str, str] | None = None) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(DaggerError):
    """Configuration-related errors."""


class ParsingError(DaggerError):
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


class UnrecognizedLineFormatError(ParsingError):
    """Error for unrecognized configuration line formats."""

    def __init__(
        self,
        line_content: str,
        device_type: str | None = None,
        expected_patterns: list[str] | None = None,
    ) -> None:
        """Initialize unrecognized line format error."""
        message = f"Unrecognized line format: {line_content.strip()}"
        if expected_patterns:
            message += f". Expected one of: {', '.join(expected_patterns)}"

        details = {"line_content": line_content}
        if expected_patterns:
            details["expected_patterns"] = ", ".join(expected_patterns)

        super().__init__(message, device_type, None, details)
        self.line_content = line_content
        self.expected_patterns = expected_patterns or []


class ContextStackError(ParsingError):
    """Error in parser context stack management."""

    def __init__(
        self,
        message: str,
        stack_depth: int,
        expected_depth: int | None = None,
        device_type: str | None = None,
    ) -> None:
        """Initialize context stack error."""
        details = {"stack_depth": str(stack_depth)}
        if expected_depth is not None:
            details["expected_depth"] = str(expected_depth)

        super().__init__(message, device_type, None, details)
        self.stack_depth = stack_depth
        self.expected_depth = expected_depth


class UnsupportedVendorError(ParsingError):
    """Error for unsupported vendor/device configurations."""

    def __init__(
        self,
        device_type: str,
        supported_types: list[str] | None = None,
    ) -> None:
        """Initialize unsupported vendor error."""
        message = f"Unsupported device type: {device_type}"
        if supported_types:
            message += f". Supported types: {', '.join(supported_types)}"

        details = {"device_type": device_type}
        if supported_types:
            details["supported_types"] = ", ".join(supported_types)

        super().__init__(message, device_type, None, details)
        self.supported_types = supported_types or []


class DatabaseError(DaggerError):
    """Database operation errors."""


class ValidationError(DaggerError):
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


class AnalysisError(DaggerError):
    """Security analysis errors."""


class ReportError(DaggerError):
    """Report generation errors."""


class UnsupportedDeviceError(DaggerError):
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


class APIError(DaggerError):
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
NetworkScannerError = DaggerError
NetworkSecurityScannerError = DaggerError
ParserError = ParsingError
NormalizationError = ValidationError
APIClientError = APIError
ReportGenerationError = ReportError
