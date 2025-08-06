"""Base parser class for all device configuration parsers."""

from abc import ABC, abstractmethod
from typing import Any


class BaseParser(ABC):
    """Abstract base class for device configuration parsers."""

    def __init__(self) -> None:
        """Initialize the parser."""
        self.parsed_data: dict[str, Any] = {}
        self.raw_config: str = ""
        self.errors: list[str] = []

    @abstractmethod
    def parse(self, config_text: str) -> dict[str, Any]:
        """Parse configuration text and return structured data.

        Args:
            config_text: Raw configuration text

        Returns:
            Structured configuration data

        Raises:
            ParsingError: If parsing fails
        """
        pass

    @abstractmethod
    def can_parse(self, config_text: str) -> bool:
        """Check if this parser can handle the given configuration.

        Args:
            config_text: Configuration text to check

        Returns:
            True if this parser can handle the config, False otherwise
        """
        pass

    def validate_config(self, config_text: str) -> bool:
        """Validate configuration syntax.

        Args:
            config_text: Configuration text to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        # Default implementation - override in subclasses
        return len(config_text.strip()) > 0

    def get_errors(self) -> list[str]:
        """Get list of parsing errors.

        Returns:
            List of error messages
        """
        return self.errors.copy()

    def clear_errors(self) -> None:
        """Clear the error list."""
        self.errors.clear()

    def _add_error(self, error_message: str) -> None:
        """Add an error message to the error list.

        Args:
            error_message: Error message to add
        """
        self.errors.append(error_message)

    def _parse_lines(self, config_text: str) -> list[str]:
        """Split configuration into lines and clean them up.

        Args:
            config_text: Raw configuration text

        Returns:
            List of cleaned configuration lines
        """
        lines = config_text.split("\n")
        # Remove trailing whitespace and empty lines
        return [line.rstrip() for line in lines if line.strip()]

    def _normalize_line(self, line: str) -> str:
        """Normalize a configuration line.

        Args:
            line: Raw configuration line

        Returns:
            Normalized configuration line
        """
        # Remove leading/trailing whitespace and convert to lowercase
        return line.strip().lower()

    def _extract_hostname(self, config_text: str) -> str | None:
        """Extract hostname from configuration.

        Args:
            config_text: Configuration text

        Returns:
            Hostname if found, None otherwise
        """
        lines = self._parse_lines(config_text)
        for line in lines:
            normalized = self._normalize_line(line)
            if normalized.startswith("hostname "):
                parts = line.strip().split()
                if len(parts) >= 2:
                    return parts[1]
        return None
