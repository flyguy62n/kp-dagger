"""Main application container for Dagger."""

from dependency_injector import containers, providers

from kp_dagger.containers.analyzers import AnalyzerContainer
from kp_dagger.containers.api_clients import ApiClientContainer
from kp_dagger.containers.core import CoreContainer
from kp_dagger.containers.parsers import ParserContainer
from kp_dagger.containers.reports import ReportContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container that orchestrates all service containers."""

    config = providers.Configuration()

    # Service containers
    core_container = providers.Container(
        CoreContainer,
        config=config.core,
    )

    api_client_container = providers.Container(
        ApiClientContainer,
        config=config.api_clients,
    )

    parser_container = providers.Container(
        ParserContainer,
        config=config.parsers,
        database_manager=core_container.database_manager,
    )

    analyzer_container = providers.Container(
        AnalyzerContainer,
        config=config.analyzers,
        database_manager=core_container.database_manager,
        api_clients=api_client_container,
    )

    report_container = providers.Container(
        ReportContainer,
        config=config.reports,
        database_manager=core_container.database_manager,
    )

    # NOTE: Main application services will be added as dependencies are implemented
    # Example for when DaggerScanner is updated:
    # scanner = providers.Factory(
    #     DaggerScanner,
    #     database_manager=core_container.database_manager,
    #     parser_factory=parser_container.parser_factory,
    #     analyzers=analyzer_container,
    #     reporters=report_container,
    #     verbose=config.scanner.verbose.as_(bool),
    # )

    def wire_modules(self) -> None:
        """Wire dependency injection to modules."""
        # NOTE: Modules will be wired as they're updated to use DI
        # self.wire(
        #     modules=[
        #         "Dagger.cli.main",
        #         "Dagger.cli.commands.analyze",
        #         "Dagger.cli.commands.report",
        #         "Dagger.cli.commands.validate",
        #     ],
        # )
