"""Parser services container for PyBastion."""

from dependency_injector import containers, providers

from kp_dagger.parsers.factory import ParserFactory


class ParserContainer(containers.DeclarativeContainer):
    """Container for parser services."""

    config = providers.Configuration()

    # External dependencies
    database_manager = providers.Dependency()

    # Parser services
    parser_factory: providers.Singleton[ParserFactory] = providers.Singleton(
        ParserFactory,
        database_manager=database_manager,
    )
