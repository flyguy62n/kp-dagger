"""Parser factory for creating device-specific parsers."""

from typing import TYPE_CHECKING

from network_security_scanner.core.exceptions import UnsupportedDeviceError
from network_security_scanner.models.base.enums import DeviceType

if TYPE_CHECKING:
    from network_security_scanner.parsers.base.parser import BaseParser


class ParserFactory:
    """Factory class for creating device-specific parsers."""

    def __init__(self) -> None:
        """Initialize the parser factory."""
        self._parsers: dict[DeviceType, type[BaseParser]] = {}
        self._register_parsers()

    def _register_parsers(self) -> None:
        """Register all available parsers."""
        # Import parsers here to avoid circular imports
        try:
            from network_security_scanner.parsers.cisco_ios.parser import CiscoIOSParser

            self._parsers[DeviceType.CISCO_IOS] = CiscoIOSParser
        except ImportError:
            pass

        try:
            from network_security_scanner.parsers.cisco_asa.parser import CiscoASAParser

            self._parsers[DeviceType.CISCO_ASA] = CiscoASAParser
        except ImportError:
            pass

        try:
            from network_security_scanner.parsers.fortigate.parser import (
                FortigateParser,
            )

            self._parsers[DeviceType.FORTIGATE] = FortigateParser
        except ImportError:
            pass

        try:
            from network_security_scanner.parsers.paloalto.parser import PaloaltoParser

            self._parsers[DeviceType.PALOALTO] = PaloaltoParser
        except ImportError:
            pass

    def get_parser(self, device_type: DeviceType) -> "BaseParser":
        """Get a parser instance for the specified device type.

        Args:
            device_type: The device type to get a parser for

        Returns:
            Parser instance for the device type

        Raises:
            UnsupportedDeviceError: If no parser is available for the device type
        """
        if device_type not in self._parsers:
            supported_types = list(self._parsers.keys())
            raise UnsupportedDeviceError(
                device_type.value, [t.value for t in supported_types]
            )

        parser_class = self._parsers[device_type]
        return parser_class()

    def get_supported_device_types(self) -> list[DeviceType]:
        """Get list of supported device types.

        Returns:
            List of supported device types
        """
        return list(self._parsers.keys())
