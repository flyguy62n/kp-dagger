"""Core services container for Dagger."""

from dependency_injector import containers, providers

from kp_dagger.core.database import DatabaseManager
from kp_dagger.core.services.events.service import EventBusService, SafeEventPublisher
from kp_dagger.core.services.file_processing.discovery import FileDiscoveryService
from kp_dagger.core.services.file_processing.encoding import (
    CharsetNormalizerEncodingDetector,
)
from kp_dagger.core.services.file_processing.hashing import SHA384FileHashGenerator
from kp_dagger.core.services.file_processing.mime_detection import MimeDetector
from kp_dagger.core.services.file_processing.service import FileProcessingService
from kp_dagger.core.services.file_processing.validation import BasicFileValidator
from kp_dagger.core.services.timestamp.service import TimestampService


class CoreContainer(containers.DeclarativeContainer):
    """Container for core Dagger services."""

    config = providers.Configuration()

    # Event bus and publisher
    event_bus_service: providers.Singleton[EventBusService] = providers.Singleton(
        EventBusService,
    )
    event_publisher: providers.Singleton[SafeEventPublisher] = providers.Singleton(
        SafeEventPublisher,
        publisher=event_bus_service,
    )

    # Timestamp service
    timestamp_service: providers.Singleton[TimestampService] = providers.Singleton(
        TimestampService,
    )

    # File processing dependencies
    encoding_detector: providers.Singleton[CharsetNormalizerEncodingDetector] = (
        providers.Singleton(CharsetNormalizerEncodingDetector)
    )
    hash_generator: providers.Singleton[SHA384FileHashGenerator] = providers.Singleton(
        SHA384FileHashGenerator,
    )
    file_validator: providers.Singleton[BasicFileValidator] = providers.Singleton(
        BasicFileValidator,
    )
    file_discovery: providers.Singleton[FileDiscoveryService] = providers.Singleton(
        FileDiscoveryService,
    )
    mime_detector: providers.Singleton[MimeDetector] = providers.Singleton(MimeDetector)

    # File processing service
    file_processing_service: providers.Singleton[FileProcessingService] = (
        providers.Singleton(
            FileProcessingService,
            encoding_detector=encoding_detector,
            hash_generator=hash_generator,
            file_validator=file_validator,
            file_discovery=file_discovery,
            mime_detector=mime_detector,
            event_publisher=event_publisher,
            timestamp_service=timestamp_service,
        )
    )

    # Database manager
    database_manager: providers.Singleton[DatabaseManager] = providers.Singleton(
        DatabaseManager,
        database_path=config.database.path.as_(str),
        # encryption_service=encryption_service,  # Will be added when implemented
    )
