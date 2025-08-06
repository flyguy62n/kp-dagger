"""
Normalized IP Address model for PyBastion.

This model represents IP addresses in a normalized format that can be used
across different device types and configurations. It supports both IPv4 and IPv6
addresses with original and normalized representations.
"""

from uuid import UUID

from sqlmodel import Field

from kp_dagger.models.base.base import PyBastionBaseModel
from kp_dagger.models.base.enums import IPVersion


class IPAddress(PyBastionBaseModel, table=True):
    """
    Normalized IP address model with encryption support.

    This model stores IP addresses with both original and normalized
    representations. The original representation preserves the exact
    format from the device configuration, while the normalized format
    provides consistent representation for analysis.
    """

    __tablename__ = "ip_addresses"

    # Basic IP address information
    version: IPVersion = Field(description="IP version (IPv4 or IPv6)")

    # Storage fields for encrypted data (not exposed in API)
    original_address_encrypted: bytes | None = Field(
        default=None,
        exclude=True,
        description="Encrypted original IP address representation",
    )
    normalized_address_encrypted: bytes | None = Field(
        default=None,
        exclude=True,
        description="Encrypted normalized IP address representation",
    )

    # Non-encrypted metadata
    prefix_length: int | None = Field(
        default=None,
        description="Network prefix length (CIDR notation)",
        ge=0,
        le=128,
    )

    is_private: bool = Field(
        default=False,
        description="Whether this is a private/internal IP address",
    )

    is_loopback: bool = Field(
        default=False,
        description="Whether this is a loopback address",
    )

    is_multicast: bool = Field(
        default=False,
        description="Whether this is a multicast address",
    )

    # Reference to source configuration
    device_id: UUID | None = Field(
        default=None,
        foreign_key="devices.id",
        description="Device this IP address was found on",
    )

    config_line_number: int | None = Field(
        default=None,
        description="Line number in configuration file where this IP was found",
    )

    context: str | None = Field(
        default=None,
        description="Configuration context (interface, ACL, route, etc.)",
    )

    # Encrypted field properties
    @property
    def original_address(self) -> str | None:
        """Get the original address (decrypted)."""
        if not hasattr(self, "_original_address_cached"):
            if self.original_address_encrypted is None:
                return None
            if self._encryption_service is None:
                msg = "Encryption service not available for decryption"
                raise RuntimeError(msg)
            try:
                self._original_address_cached = self._encryption_service.decrypt(
                    self.original_address_encrypted,
                )
            except Exception:  # noqa: BLE001
                return None
        return self._original_address_cached

    @original_address.setter
    def original_address(self, value: str | None) -> None:
        """Set the original address (encrypted)."""
        if value is None:
            self.original_address_encrypted = None
            self._original_address_cached = None
            return

        if self._encryption_service is None:
            msg = "Encryption service not available for encryption"
            raise RuntimeError(msg)

        self.original_address_encrypted = self._encryption_service.encrypt(value)
        self._original_address_cached = value

    @property
    def normalized_address(self) -> str | None:
        """Get the normalized address (decrypted)."""
        if not hasattr(self, "_normalized_address_cached"):
            if self.normalized_address_encrypted is None:
                return None
            if self._encryption_service is None:
                msg = "Encryption service not available for decryption"
                raise RuntimeError(msg)
            try:
                self._normalized_address_cached = self._encryption_service.decrypt(
                    self.normalized_address_encrypted,
                )
            except Exception:  # noqa: BLE001
                return None
        return self._normalized_address_cached

    @normalized_address.setter
    def normalized_address(self, value: str | None) -> None:
        """Set the normalized address (encrypted)."""
        if value is None:
            self.normalized_address_encrypted = None
            self._normalized_address_cached = None
            return

        if self._encryption_service is None:
            msg = "Encryption service not available for encryption"
            raise RuntimeError(msg)

        self.normalized_address_encrypted = self._encryption_service.encrypt(value)
        self._normalized_address_cached = value
