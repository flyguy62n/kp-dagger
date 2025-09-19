"""Data models for parsing device configurations."""

from pydantic import Field

from kp_dagger.models.base import KPDaggerBaseModel
from kp_dagger.models.base.types import ConfigContent


class DeviceConfigMetadata(KPDaggerBaseModel):
    """Configuration parsing metadata."""

    total_lines: int
    parsed_lines: int
    unparsed_lines: list[str] = Field(default_factory=list)  # Safe mutable default


class ParsedDeviceConfig(KPDaggerBaseModel):
    """Complete configuration in generic structure preserving vendor format."""

    content: ConfigContent  # Structured but flexible - vendor determines organization
    metadata: DeviceConfigMetadata
    raw_text: str
