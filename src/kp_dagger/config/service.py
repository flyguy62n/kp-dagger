"""Configuration service using DynaConf and Pydantic validation."""

import logging
from functools import lru_cache
from pathlib import Path

from dynaconf import Dynaconf
from pydantic import ValidationError

from kp_dagger.models.base.enums import DeviceType
from kp_dagger.models.config import DaggerConfig, ParserConfig

logger = logging.getLogger(__name__)


class ConfigurationService:
    """
    Configuration service providing typed access to application settings.

    Uses DynaConf for multi-file YAML loading with environment support
    and Pydantic for type-safe validation and access patterns.

    This is a simple, non-DI service that can be used directly in CLI
    commands or injected via DI when needed by services.
    """

    def __init__(
        self,
        config_dir: str | Path = "config",
        environment: str | None = None,
    ) -> None:
        """
        Initialize configuration service.

        Args:
            config_dir: Directory containing YAML configuration files
            environment: Environment name for dynaconf (dev, prod, test)

        """
        self.config_dir = Path(config_dir)
        self.environment = environment

        # Initialize DynaConf with multiple file support
        self._dynaconf = Dynaconf(
            settings_files=[
                str(self.config_dir / "settings.yaml"),
                str(self.config_dir / "parsers.yaml"),
                str(self.config_dir / "*.yaml"),
                str(self.config_dir / "*.yml"),
            ],
            environments=False,  # Disable for simpler setup
            load_dotenv=True,
            envvar_prefix="DAGGER",  # DAGGER_FOO__BAR overrides foo.bar
        )

        # Validate and cache the configuration
        self._config = self._load_and_validate()

    def _load_and_validate(self) -> DaggerConfig:
        """Load configuration from DynaConf and validate with Pydantic."""
        try:
            # Extract only the expected configuration sections
            config_dict = {
                "parsers": self._dynaconf.parsers or {},
            }
            logger.debug("Loaded configuration from %s", self.config_dir)

            # Validate with Pydantic
            return DaggerConfig.model_validate(config_dict)

        except ValidationError as e:
            logger.exception("Configuration validation failed")
            msg = f"Invalid configuration: {e}"
            raise ConfigurationError(msg) from e
        except Exception as e:
            logger.exception("Failed to load configuration")
            msg = f"Configuration loading failed: {e}"
            raise ConfigurationError(msg) from e

    @property
    def config(self) -> DaggerConfig:
        """Get the validated application configuration."""
        return self._config

    def get_parser_config(self, device_type: DeviceType) -> ParserConfig | None:
        """
        Get configuration for a specific device parser.

        Args:
            device_type: The device type to get parser config for

        Returns:
            ParserConfig if found and enabled, None otherwise

        """
        parser_key = device_type.value.replace("-", "_")
        return self._config.parsers.get(parser_key)

    def get_enabled_parsers(self) -> dict[DeviceType, ParserConfig]:
        """
        Get all enabled parser configurations.

        Returns:
            Dictionary mapping DeviceType to ParserConfig for enabled parsers

        """
        return self._config.get_enabled_parsers()

    def is_parser_enabled(self, device_type: DeviceType) -> bool:
        """
        Check if a parser is enabled for the given device type.

        Args:
            device_type: The device type to check

        Returns:
            True if parser is configured and enabled

        """
        return self._config.is_parser_enabled(device_type)

    def reload(self) -> None:
        """
        Reload configuration from files.

        Useful for development or when configuration files change.
        """
        # Recreate DynaConf instance to reload files
        self.__init__(self.config_dir, self.environment)
        self._config = self._load_and_validate()
        logger.info("Configuration reloaded from %s", self.config_dir)


class ConfigurationError(Exception):
    """Raised when configuration loading or validation fails."""


@lru_cache(maxsize=1)
def get_configuration_service(
    config_dir: str = "config",
    environment: str | None = None,
) -> ConfigurationService:
    """
    Get a cached configuration service instance.

    This provides a simple singleton pattern for cases where you want
    to avoid creating multiple ConfigurationService instances.

    Args:
        config_dir: Directory containing configuration files
        environment: Environment name (dev, prod, test)

    Returns:
        Cached ConfigurationService instance

    """
    return ConfigurationService(config_dir=config_dir, environment=environment)
