"""Common SQLModel mixins."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin for timestamp fields."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)


class DeviceReferenceMixin(SQLModel):
    """Mixin for device reference fields."""

    device_id: str = Field(foreign_key="devices.id")
    device_type: str
    device_hostname: str | None = None
