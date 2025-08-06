"""Analyzer services container for PyBastion."""

from dependency_injector import containers, providers


class AnalyzerContainer(containers.DeclarativeContainer):
    """Container for analyzer services."""

    config = providers.Configuration()

    # External dependencies
    database_manager: providers.Dependency[object] = providers.Dependency()
    api_clients: providers.Dependency[object] = providers.Dependency()

    # NOTE: Analyzer services will be added as the actual service classes are implemented
    # Example structure for future implementation:
    #
    # compliance_analyzer = providers.Factory(
    #     ComplianceAnalyzer,
    #     database_manager=database_manager,
    #     config=config.compliance,
    # )
    #
    # vulnerability_analyzer = providers.Factory(
    #     VulnerabilityAnalyzer,
    #     database_manager=database_manager,
    #     cve_client=api_clients.cve_client,
    #     eol_client=api_clients.eol_client,
    # )
    #
    # risk_analyzer = providers.Factory(
    #     RiskAnalyzer,
    #     database_manager=database_manager,
    #     config=config.risk,
    # )
