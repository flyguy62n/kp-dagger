"""API client services container for Dagger."""

from dependency_injector import containers, providers


class ApiClientContainer(containers.DeclarativeContainer):
    """Container for external API client services."""

    config = providers.Configuration()

    # TODO: Implement actual API clients when modules are created
    # API clients will be added as the actual service classes are implemented
    # Example structure for future implementation:
    #
    # cve_client = providers.Singleton(
    #     CveClient,
    #     api_key=config.cve.api_key.as_(str),
    #     base_url=config.cve.base_url.as_(str),
    #     timeout=config.cve.timeout.as_(int),
    #     rate_limit=config.cve.rate_limit.as_(int),
    # )
    #
    # eol_client = providers.Singleton(
    #     EolClient,
    #     base_url=config.eol.base_url.as_(str),
    #     timeout=config.eol.timeout.as_(int),
    #     rate_limit=config.eol.rate_limit.as_(int),
    # )
