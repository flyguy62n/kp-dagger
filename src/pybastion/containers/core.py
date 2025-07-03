"""Core services container for PyBastion."""

from dependency_injector import containers, providers

from pybastion.core.database import DatabaseManager


class CoreContainer(containers.DeclarativeContainer):
    """Container for core PyBastion services."""

    config = providers.Configuration()

    # Core services
    # NOTE: EncryptionService will be added when implemented
    # encryption_service = providers.Singleton(
    #     EncryptionService,
    #     master_key=config.encryption.master_key.as_(str),
    #     salt=config.encryption.salt.as_(str),
    # )

    database_manager: providers.Singleton[DatabaseManager] = providers.Singleton(
        DatabaseManager,
        database_path=config.database.path.as_(str),
        # encryption_service=encryption_service,  # Will be added when implemented
    )
