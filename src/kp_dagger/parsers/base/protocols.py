"""Base parser class for all device configuration parsers."""

from typing import Protocol

from kp_dagger.models.base.device_config import ParsedDeviceConfig


class DeviceParser(Protocol):
    """Protocol for device configuration parsers."""

    def parse_config(self, config_text: str) -> ParsedDeviceConfig:
        """Extract all configuration data into generic structure using parameter=value patterns."""
        ...
