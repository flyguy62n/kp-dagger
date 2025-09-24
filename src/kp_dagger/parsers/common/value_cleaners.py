"""Common value cleaning utilities for network device configuration parsers."""

import re
from typing import Any

# IP address detection constants
IPV4_PATTERN = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d{1,2})?$")
IPV6_MIN_PARTS = 4  # Minimum colon-separated parts to distinguish from port numbers
MIN_QUOTE_LENGTH = 2  # Minimum length for quoted strings
IPV6_PATTERNS = [
    re.compile(r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"),  # Full IPv6
    re.compile(r"^::1$"),  # Loopback
    re.compile(r"^::$"),  # All zeros
    re.compile(
        r"^([0-9a-fA-F]{1,4}:)*::([0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}$",
    ),  # Compressed
    re.compile(r"^([0-9a-fA-F]{1,4}:)*::[0-9a-fA-F]{1,4}$"),  # Leading compression
    re.compile(
        r"^[0-9a-fA-F]{1,4}::([0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}$",
    ),  # Trailing compression
]

# Common boolean values across vendors
BOOLEAN_VALUES = {
    # FortiGate
    "enable": True,
    "disable": False,
    # Cisco
    "true": True,
    "false": False,
    "yes": True,
    "no": False,
    "on": True,
    "off": False,
    # SonicWall
    "enabled": True,
    "disabled": False,
}


def is_ipv4_address(value: str) -> bool:
    """Check if value is an IPv4 address (with optional CIDR)."""
    return bool(IPV4_PATTERN.match(value))


def is_ipv6_address(value: str) -> bool:
    """
    Check if value is an IPv6 address.

    Uses multiple patterns to catch various IPv6 formats including compressed notation.
    """
    if ":" not in value:
        return False

    # Simple heuristic: if it has colons and enough parts, likely IPv6
    parts = value.split(":")
    if "::" in value or len(parts) > IPV6_MIN_PARTS:
        # Validate with regex patterns
        return any(pattern.match(value) for pattern in IPV6_PATTERNS)

    return False


def is_ip_address(value: str) -> bool:
    """Check if value is any type of IP address."""
    return is_ipv4_address(value) or is_ipv6_address(value)


def clean_quoted_value(value: str) -> str:
    """Remove surrounding quotes from configuration values."""
    value = value.strip()

    # Remove surrounding quotes (single or double)
    if len(value) >= MIN_QUOTE_LENGTH and (
        (value.startswith('"') and value.endswith('"'))
        or (value.startswith("'") and value.endswith("'"))
    ):
        value = value[1:-1]

    return value


def convert_boolean_value(value: str) -> bool | None:
    """
    Convert string to boolean if it matches known boolean patterns.

    Returns None if the value is not a recognized boolean.
    """
    value_lower = value.lower()
    return BOOLEAN_VALUES.get(value_lower)


def convert_numeric_value(value: str) -> int | float | None:
    """
    Convert string to number if possible.

    Returns None if the value is not numeric.
    """
    try:
        # Try integer first
        if "." not in value and "e" not in value.lower():
            return int(value)
        # Try float
        return float(value)
    except ValueError:
        return None


def clean_configuration_value(value: str) -> str | bool | int | float:
    """
    Clean and convert a configuration value using common network device patterns.

    This is the main entry point for value cleaning that handles:
    - Quote removal
    - Boolean conversion
    - Numeric conversion
    - IP address preservation
    - Default string return
    """
    # Start with quote removal
    cleaned = clean_quoted_value(value)

    # Handle empty values
    if not cleaned:
        return cleaned

    # Check for boolean values first
    bool_value = convert_boolean_value(cleaned)
    if bool_value is not None:
        return bool_value

    # Preserve IP addresses as strings (don't try to convert to numbers)
    if is_ip_address(cleaned):
        return cleaned

    # Try numeric conversion
    numeric_value = convert_numeric_value(cleaned)
    if numeric_value is not None:
        return numeric_value

    # Return as string if nothing else matches
    return cleaned


class VendorSpecificCleaner:
    """
    Base class for vendor-specific value cleaning with common functionality.

    Subclasses can override specific methods while inheriting common patterns.
    """

    def __init__(self) -> None:
        # Vendors can extend these mappings
        self.additional_booleans: dict[str, bool] = {}
        self.special_patterns: dict[str, Any] = {}

    def clean_value(self, value: str) -> str | bool | int | float:
        """
        Clean value with vendor-specific overrides.

        Override this method in subclasses for vendor-specific behavior.
        """
        # First try vendor-specific patterns
        result = self._apply_vendor_patterns(value)
        if result is not None:
            return result

        # Fall back to common cleaning
        return clean_configuration_value(value)

    def _apply_vendor_patterns(self, value: str) -> str | bool | int | float | None:
        """
        Apply vendor-specific patterns.

        Override in subclasses. Return None to fall back to common cleaning.
        """
        # Check additional boolean mappings
        cleaned = clean_quoted_value(value)
        bool_value = self.additional_booleans.get(cleaned.lower())
        if bool_value is not None:
            return bool_value

        # Check special patterns
        for pattern, converter in self.special_patterns.items():
            if re.match(pattern, cleaned):
                return converter(cleaned)

        return None


class FortigateCleaner(VendorSpecificCleaner):
    """FortiGate-specific value cleaner."""

    def __init__(self) -> None:
        super().__init__()
        # FortiGate uses the standard enable/disable pattern
        # No additional patterns needed currently


class CiscoCleaner(VendorSpecificCleaner):
    """Cisco (ASA/IOS) specific value cleaner."""

    def __init__(self) -> None:
        super().__init__()
        # Cisco has some unique boolean patterns
        self.additional_booleans.update(
            {
                "shutdown": False,
                "no shutdown": True,
                "up": True,
                "down": False,
            },
        )

        # Cisco-specific patterns (placeholder for future)
        self.special_patterns.update(
            {
                # Could add patterns for Cisco-specific formats
            },
        )


class SonicWallCleaner(VendorSpecificCleaner):
    """SonicWall-specific value cleaner."""

    def __init__(self) -> None:
        super().__init__()
        # SonicWall boolean patterns
        self.additional_booleans.update(
            {
                "allow": True,
                "deny": False,
                "drop": False,
            },
        )
