"""Parser factory for creating device-specific parsers."""

from typing import TYPE_CHECKING

from kp_dagger.core.exceptions import UnsupportedDeviceError
from kp_dagger.core.services.events import SafeEventPublisher
from kp_dagger.core.services.file_processing import FileProcessor
from kp_dagger.core.services.timestamp import TimestampService
from kp_dagger.models.base.enums import DeviceType
from kp_dagger.models.events import OperationCompleted, OperationError, OperationStarted
from kp_dagger.parsers.base.protocols import ConfigurationParser

if TYPE_CHECKING:
    from kp_dagger.config.service import ConfigurationService


class ParserFactory:
    """Factory class for creating device-specific parsers with dependency injection."""

    def __init__(
        self,
        file_processing_service: FileProcessor,
        event_publisher: SafeEventPublisher,
        timestamp_service: TimestampService,
        configuration_service: "ConfigurationService",
    ) -> None:
        """Initialize the parser factory with required services."""
        self._file_processing_service = file_processing_service
        self._event_publisher = event_publisher
        self._timestamp_service = timestamp_service
        self._configuration_service = configuration_service

        self._parsers: dict[DeviceType, type[ConfigurationParser]] = {}
        self._register_parsers()

    def _register_parsers(self) -> None:
        """Register parsers based on configuration service settings."""
        # Get enabled parsers from configuration
        enabled_parsers = self._configuration_service.get_enabled_parsers()

        # Publish parser registration start event
        start_time = self._timestamp_service.utc_now()
        self._event_publisher.publish(
            OperationStarted(
                operation_type="parser_registration",
                context={
                    "enabled_parsers_count": len(enabled_parsers),
                    "parser_types": [parser.value for parser in enabled_parsers]
                    if enabled_parsers
                    else [],
                },
            ),
        )

        registered_count = 0
        errors = []

        for device_type, parser_config in enabled_parsers.items():
            # Use configuration to dynamically load parser
            try:
                # Import parser module and get parser class
                import importlib

                # Debug: Log what we're trying to load
                self._event_publisher.publish(
                    OperationStarted(
                        operation_type="parser_load",
                        context={
                            "device_type": device_type.value,
                            "module": parser_config.module,
                            "class_name": parser_config.class_name,
                        },
                    ),
                )

                parser_module = importlib.import_module(parser_config.module)
                parser_class = getattr(parser_module, parser_config.class_name)

                # Register the parser class
                self._parsers[device_type] = parser_class
                registered_count += 1

                # Publish successful parser registration
                self._event_publisher.publish(
                    OperationCompleted(
                        operation_type="parser_registration",
                        success=True,
                        duration=self._timestamp_service.elapsed_seconds(start_time),
                        results={
                            "device_type": device_type.value,
                            "parser_class": parser_config.class_name,
                            "parser_module": parser_config.module,
                            "cleaner_class": parser_config.cleaner,
                            "enabled": parser_config.enabled,
                        },
                    ),
                )
            except (ImportError, AttributeError, ModuleNotFoundError) as e:
                error_msg = f"{device_type.value} parser registration failed: {e}"
                errors.append(error_msg)
                self._event_publisher.publish(
                    OperationError(
                        operation_type="parser_registration",
                        error_message=error_msg,
                        error_context={
                            "device_type": device_type.value,
                            "parser_module": parser_config.module,
                            "parser_class": parser_config.class_name,
                            "cleaner_class": parser_config.cleaner,
                            "error_type": type(e).__name__,
                        },
                    ),
                )

        # Publish overall registration completion
        duration = self._timestamp_service.elapsed_seconds(start_time)
        self._event_publisher.publish(
            OperationCompleted(
                operation_type="parser_registration",
                success=len(errors) == 0,
                duration=duration,
                results={
                    "total_enabled": len(enabled_parsers),
                    "successfully_registered": registered_count,
                    "errors_count": len(errors),
                    "registered_parsers": [dt.value for dt in self._parsers],
                    "errors_list": errors,
                },
            ),
        )

    def get_parser(self, device_type: DeviceType) -> ConfigurationParser:
        """
        Get a parser instance for the specified device type.

        Args:
            device_type: The device type to get a parser for

        Returns:
            Parser instance for the device type

        Raises:
            UnsupportedDeviceError: If no parser is available for the device type

        """
        if device_type not in self._parsers:
            supported_types = list(self._parsers.keys())
            raise UnsupportedDeviceError(
                device_type.value,
                [t.value for t in supported_types],
            )

        parser_class = self._parsers[device_type]

        # Create parser with dependencies using configuration
        parser_config = self._configuration_service.get_parser_config(device_type)
        if parser_config is None:
            # Fallback - should not happen if registration worked correctly
            return parser_class()

        try:
            # Import cleaner class dynamically
            import importlib
            import inspect

            cleaner_module = importlib.import_module(
                "kp_dagger.parsers.common.value_cleaners",
            )
            cleaner_class = getattr(cleaner_module, parser_config.cleaner)
            value_cleaner = cleaner_class()

            # Use inspect to check constructor parameters
            parser_signature = inspect.signature(parser_class.__init__)
            parser_params = set(parser_signature.parameters.keys()) - {"self"}

            # Build kwargs based on what the parser actually accepts
            kwargs = {}
            if "file_processing_service" in parser_params:
                kwargs["file_processing_service"] = self._file_processing_service
            if "event_publisher" in parser_params:
                kwargs["event_publisher"] = self._event_publisher
            if "timestamp_service" in parser_params:
                kwargs["timestamp_service"] = self._timestamp_service
            if "value_cleaner" in parser_params:
                kwargs["value_cleaner"] = value_cleaner

            return parser_class(**kwargs)

        except (ImportError, AttributeError, TypeError) as e:
            # If dynamic instantiation fails, try without dependencies
            # This provides fallback for parsers that don't follow the standard constructor
            try:
                return parser_class()
            except (TypeError, AttributeError) as fallback_error:
                # Re-raise the original error if fallback also fails
                raise UnsupportedDeviceError(
                    device_type.value,
                    [
                        f"Failed to instantiate parser: {e}. Fallback also failed: {fallback_error}",
                    ],
                ) from e

    def get_supported_device_types(self) -> list[DeviceType]:
        """
        Get list of supported device types.

        Returns:
            List of supported device types

        """
        return list(self._parsers.keys())
