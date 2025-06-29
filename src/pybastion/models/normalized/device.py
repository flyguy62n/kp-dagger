"""Device metadata and information models."""

from pybastion.models.base.enums import DeviceType
from pybastion.models.base.mixins import TimestampMixin
from sqlmodel import Field, SQLModel


class Device(SQLModel, TimestampMixin, table=True):
    """Device information and metadata."""

    __tablename__ = "devices"

    id: str = Field(primary_key=True)
    hostname: str
    device_type: DeviceType
    vendor: str | None = None
    model: str | None = None
    version: str | None = None
    serial_number: str | None = None
    management_ip: str | None = None
    location: str | None = None
    description: str | None = None
    is_active: bool = Field(default=True)
