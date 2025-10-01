"""Parser services container for Dagger."""

from dependency_injector import containers, providers

from kp_dagger.parsers.factory import ParserFactory


class ParserContainer(containers.DeclarativeContainer):
    """Container for parser services."""

    config = providers.Configuration()

    # External dependencies from core container
    file_processing_service = providers.Dependency()
    event_publisher = providers.Dependency()
    timestamp_service = providers.Dependency()

    # External dependency: ConfigurationService (injected from CLI or other contexts)
    configuration_service = providers.Dependency()

    # Parser factory with all required dependencies
    # Note: Value cleaners are now created dynamically within the factory based on parser type
    parser_factory: providers.Singleton[ParserFactory] = providers.Singleton(
        ParserFactory,
        file_processing_service=file_processing_service,
        event_publisher=event_publisher,
        timestamp_service=timestamp_service,
        configuration_service=configuration_service,
    )
