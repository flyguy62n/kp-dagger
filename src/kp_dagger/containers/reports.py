"""Report services container for Dagger."""

from dependency_injector import containers, providers


class ReportContainer(containers.DeclarativeContainer):
    """Container for report generation services."""

    config = providers.Configuration()

    # External dependencies
    database_manager: providers.Dependency[object] = providers.Dependency()

    # NOTE: Report services will be added as the actual service classes are implemented
    # Example structure for future implementation:
    #
    # json_reporter = providers.Factory(
    #     JsonReporter,
    #     database_manager=database_manager,
    # )
    #
    # html_reporter = providers.Factory(
    #     HtmlReporter,
    #     database_manager=database_manager,
    #     template_path=config.templates.html_path.as_(str),
    # )
    #
    # excel_reporter = providers.Factory(
    #     ExcelReporter,
    #     database_manager=database_manager,
    #     template_path=config.templates.excel_path.as_(str),
    # )
