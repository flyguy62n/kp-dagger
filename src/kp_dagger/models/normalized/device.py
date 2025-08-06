"""Device metadata and information models."""

from uuid import UUID

from sqlmodel import Field

from kp_dagger.models.base.base import DaggerBaseModel
from kp_dagger.models.base.enums import DeviceType


class Device(DaggerBaseModel, table=True):
    """Device information and metadata."""

    __tablename__ = "devices"

    hostname: str = Field(
        description="Device hostname as configured",
    )

    device_type: DeviceType = Field(
        description="Type of network device",
    )

    vendor: str | None = Field(
        default=None,
        description="Device vendor/manufacturer",
    )

    model: str | None = Field(
        default=None,
        description="Device model",
    )

    version: str | None = Field(
        default=None,
        description="Software/firmware version",
    )

    serial_number: str | None = Field(
        default=None,
        description="Device serial number",
    )

    management_ip_id: UUID | None = Field(
        default=None,
        foreign_key="ip_addresses.id",
        description="Reference to management IP address",
    )

    location: str | None = Field(
        default=None,
        description="Physical location of the device",
    )

    description: str | None = Field(
        default=None,
        description="Device description or notes",
    )

    is_active: bool = Field(
        default=True,
        description="Whether this device is currently active",
    )
