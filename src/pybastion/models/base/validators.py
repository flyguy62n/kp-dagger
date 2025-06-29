"""Pydantic validators for network concepts."""

import re
from typing import ClassVar


class NetworkValidators:
    """Collection of network-related validators."""

    # Common port range pattern
    PORT_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^\d+(-\d+)?$")
    MAX_PORT_NUMBER: ClassVar[int] = 65535

    @classmethod
    def validate_port(cls, value: str) -> str:
        """Validate port number or range."""
        if not cls.PORT_PATTERN.match(value):
            msg = f"Invalid port format: {value}"
            raise ValueError(msg)

        # Check individual port numbers
        if "-" in value:
            start, end = value.split("-")
            start_port, end_port = int(start), int(end)
        else:
            start_port = end_port = int(value)

        max_port = cls.MAX_PORT_NUMBER
        if not (0 <= start_port <= max_port) or not (0 <= end_port <= max_port):
            msg = f"Port numbers must be between 0 and {max_port}: {value}"
            raise ValueError(msg)

        if start_port > end_port:
            msg = f"Start port must be less than or equal to end port: {value}"
            raise ValueError(msg)

        return value

    @classmethod
    def validate_protocol(cls, value: str) -> str:
        """Validate protocol name."""
        valid_protocols = {
            "tcp",
            "udp",
            "icmp",
            "esp",
            "ah",
            "gre",
            "ospf",
            "eigrp",
            "ip",
            "any",
        }

        if value.lower() not in valid_protocols:
            msg = f"Invalid protocol: {value}. Valid protocols: {valid_protocols}"
            raise ValueError(msg)

        return value.lower()
