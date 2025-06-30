"""
Foundational IP Address model for PyBastion.

This module defines the IPAddress model that serves as the foundation
for all IP address representations throughout the application.
"""

import ipaddress

from pydantic import ValidationInfo, field_validator
from sqlmodel import Field, Index, UniqueConstraint

from pybastion.models.base.base import PyBastionBaseModel
from pybastion.models.base.enums import AddressType, IPVersion

# Constants for IP prefix length validation
IPV4_MAX_PREFIX_LENGTH = 32
IPV6_MAX_PREFIX_LENGTH = 128


class IPAddress(PyBastionBaseModel, table=True):
    """
    Foundational IP Address model for PyBastion.

    Stores both original vendor representation and normalized form
    for traceability and consistency across different device types.
    """

    __tablename__ = "ip_addresses"

    # Core IP address information (normalized)
    ip_address: str = Field(
        description="The IP address in canonical form (e.g., '192.168.1.1')",
    )

    prefix_length: int | None = Field(
        default=None,
        description="CIDR prefix length (e.g., 24 for /24), None for host addresses",
    )

    netmask: str | None = Field(
        default=None,
        description="Dotted decimal netmask (e.g., '255.255.255.0'), None for host addresses",
    )

    ip_version: IPVersion = Field(
        description="IP version (IPv4 or IPv6)",
    )

    address_type: AddressType = Field(
        description="Type of address representation (individual, network, range, etc.)",
    )

    # Original representation for traceability
    original_format: str = Field(
        description="Exact format as it appeared in configuration (e.g., '192.168.1.1 255.255.255.0', 'host 192.168.1.100', 'any')",
    )

    # Computed/derived fields for efficiency
    network_address: str | None = Field(
        default=None,
        description="Network portion (e.g., '192.168.1.0'), computed from ip_address and prefix_length",
    )

    broadcast_address: str | None = Field(
        default=None,
        description="Broadcast address (IPv4 only), None for IPv6 or host addresses",
    )

    host_count: int | None = Field(
        default=None,
        description="Number of host addresses in network, None for individual addresses",
    )

    # Context and metadata
    description: str | None = Field(
        default=None,
        description="Human-readable description or comment",
    )

    is_private: bool = Field(
        default=False,
        description="True if address is in RFC 1918 private address space",
    )

    is_multicast: bool = Field(
        default=False,
        description="True if address is multicast",
    )

    is_reserved: bool = Field(
        default=False,
        description="True if address is reserved/special use",
    )

    # Database constraints and indexes
    __table_args__ = (
        UniqueConstraint(
            "customer_id",
            "ip_address",
            "prefix_length",
            "address_type",
            name="unique_ip_per_customer",
        ),
        Index("idx_customer_ip", "customer_id", "ip_address"),
        Index("idx_customer_network", "customer_id", "network_address"),
        Index("idx_ip_version", "ip_version"),
        Index("idx_address_type", "address_type"),
    )

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, value: str) -> str:
        """Validate IP address format."""
        try:
            ipaddress.ip_address(value)
        except ValueError as exc:
            msg = f"Invalid IP address: {value}"
            raise ValueError(msg) from exc
        return value

    @field_validator("netmask")
    @classmethod
    def validate_netmask(cls, value: str | None) -> str | None:
        """Validate netmask format."""
        if value is None:
            return value
        try:
            # Validate netmask by trying to parse as IP address
            ipaddress.ip_address(value)
        except ValueError as exc:
            msg = f"Invalid netmask: {value}"
            raise ValueError(msg) from exc
        return value

    @field_validator("prefix_length")
    @classmethod
    def validate_prefix_length(
        cls, value: int | None, info: ValidationInfo
    ) -> int | None:
        """Validate prefix length based on IP version."""
        if value is None:
            return value

        # Get IP version from the model data
        ip_version = info.data.get("ip_version") if info.data else None

        if ip_version == IPVersion.IPV4 and not (0 <= value <= IPV4_MAX_PREFIX_LENGTH):
            msg = f"IPv4 prefix length must be between 0 and {IPV4_MAX_PREFIX_LENGTH}, got {value}"
            raise ValueError(msg)
        if ip_version == IPVersion.IPV6 and not (0 <= value <= IPV6_MAX_PREFIX_LENGTH):
            msg = f"IPv6 prefix length must be between 0 and {IPV6_MAX_PREFIX_LENGTH}, got {value}"
            raise ValueError(msg)

        return value

    def __str__(self) -> str:
        """String representation of the IP address."""
        if self.prefix_length is not None:
            return f"{self.ip_address}/{self.prefix_length}"
        return self.ip_address

    def __repr__(self) -> str:
        """Detailed representation of the IP address."""
        return f"IPAddress(ip_address='{self.ip_address}', type='{self.address_type}', original='{self.original_format}')"
