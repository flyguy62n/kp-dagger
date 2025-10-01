"""Base parser protocols for all device configuration parsers."""

from typing import Any, Protocol

from kp_dagger.models.base.types import PathLike


class ConfigurationParser(Protocol):
    """Protocol for device configuration parsers."""

    def parse_file(self, file_path: PathLike) -> dict[str, Any]:
        """
        Parse a configuration file and return structured data.

        Args:
            file_path: Path to the configuration file

        Returns:
            Dictionary containing parsed configuration data

        """
        ...
