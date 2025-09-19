"""Shared type definitions for device configuration processing."""

from typing import TypeGuard

# Core configuration value types
ConfigValue = str | int | float | bool | list[str] | dict[str, "ConfigValue"]
ConfigSection = dict[str, ConfigValue]
ConfigContent = dict[str, ConfigValue | ConfigSection | list[ConfigSection]]


# Type guards for safe runtime checking
def is_config_section(value: ConfigValue) -> TypeGuard[ConfigSection]:
    """Type guard to check if value is a configuration section."""
    return isinstance(value, dict)


def is_config_list(value: ConfigValue) -> TypeGuard[list[ConfigSection]]:
    """Type guard to check if value is a list of configuration sections."""
    return isinstance(value, list) and all(isinstance(item, dict) for item in value)


def is_string_list(value: ConfigValue) -> TypeGuard[list[str]]:
    """Type guard to check if value is a list of strings."""
    return isinstance(value, list) and all(isinstance(item, str) for item in value)
