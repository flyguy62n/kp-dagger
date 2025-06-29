"""FortiGate configuration parser."""

from typing import Any

from network_security_scanner.parsers.base.parser import BaseParser


class FortigateParser(BaseParser):
    """Parser for FortiGate device configurations."""

    def parse(self, config_text: str) -> dict[str, Any]:
        """Parse FortiGate configuration text.

        Args:
            config_text: Raw configuration text

        Returns:
            Structured configuration data
        """
        # TODO: Implement FortiGate parsing logic
        return {
            "device_type": "fortigate",
            "hostname": self._extract_hostname(config_text),
        }

    def can_parse(self, config_text: str) -> bool:
        """Check if this parser can handle the given configuration.

        Args:
            config_text: Configuration text to check

        Returns:
            True if this parser can handle the config, False otherwise
        """
        # TODO: Implement device detection logic
        config_lower = config_text.lower()
        return any(
            pattern in config_lower
            for pattern in ["config system", "config firewall", "edit ", "next", "end"]
        )
