"""Common types used throughout the Dagger."""

from kp_dagger.models.base.types.addresses import IPAddress, NetworkAddress
from kp_dagger.models.base.types.device_config import (
    ConfigContent,
    ConfigSection,
    ConfigValue,
    is_config_list,
    is_config_section,
    is_string_list,
)
from kp_dagger.models.base.types.paths import PathLike

__all__: list[str] = [
    "ConfigContent",
    "ConfigSection",
    "ConfigValue",
    "IPAddress",
    "NetworkAddress",
    "PathLike",
    "is_config_list",
    "is_config_section",
    "is_string_list",
]
