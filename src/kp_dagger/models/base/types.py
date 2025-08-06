"""Custom field types for network concepts."""

import ipaddress
from collections.abc import Generator


class IPAddress(str):
    """Custom type for IP addresses with validation."""

    __slots__ = ()

    @classmethod
    def __get_validators__(cls) -> Generator:
        """Get Pydantic validators."""
        yield cls.validate

    @classmethod
    def validate(cls, value: object) -> str:
        """Validate IP address format."""
        if isinstance(value, str):
            try:
                ipaddress.ip_address(value)
            except ValueError as exc:
                msg = f"Invalid IP address: {value}"
                raise ValueError(msg) from exc
            else:
                return value
        msg = f"IP address must be string, got {type(value)}"
        raise ValueError(msg)


class NetworkAddress(str):
    """Custom type for network addresses (CIDR notation)."""

    __slots__ = ()

    @classmethod
    def __get_validators__(cls) -> Generator:
        """Get Pydantic validators."""
        yield cls.validate

    @classmethod
    def validate(cls, value: object) -> str:
        """Validate network address format."""
        if isinstance(value, str):
            try:
                ipaddress.ip_network(value, strict=False)
            except ValueError as exc:
                msg = f"Invalid network address: {value}"
                raise ValueError(msg) from exc
            else:
                return value
        msg = f"Network address must be string, got {type(value)}"
        raise ValueError(msg)
