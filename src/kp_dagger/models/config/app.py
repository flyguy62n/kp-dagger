"""Application configuration models for Dagger."""

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from kp_dagger.models.base.enums import DeviceType
from kp_dagger.models.config.parsers import ParserConfig


class DaggerConfig(BaseModel):
    """Main Dagger application configuration."""

    parsers: dict[str, ParserConfig] = Field(default_factory=dict)

    @classmethod
    @field_validator("parsers")
    def validate_parser_keys(
        cls,
        v: dict[str, ParserConfig],
    ) -> dict[str, ParserConfig]:
        """Validate that parser keys correspond to valid device types."""
        for parser_key in v:
            try:
                # Convert parser key to device type (handle underscores -> hyphens)
                device_type_value = parser_key.replace("_", "-")
                DeviceType(device_type_value)
            except ValueError:
                msg = (
                    f'Parser key "{parser_key}" does not correspond to a valid device type. '
                    f"Valid types: {[dt.value for dt in DeviceType]}"
                )
                raise ValueError(msg) from None
        return v

    def get_enabled_parsers(self) -> dict[DeviceType, ParserConfig]:
        """Get only the enabled parsers mapped to their DeviceType."""
        enabled = {}
        for parser_key, parser_config in self.parsers.items():
            if parser_config.enabled:
                device_type_value = parser_key.replace("_", "-")
                device_type = DeviceType(device_type_value)
                enabled[device_type] = parser_config
        return enabled

    def is_parser_enabled(self, device_type: DeviceType) -> bool:
        """Check if a specific parser is enabled."""
        parser_key = device_type.value.replace("-", "_")
        parser_config = self.parsers.get(parser_key)
        return parser_config is not None and parser_config.enabled

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
