"""Simple test for dependency injection without full app dependencies."""

from dependency_injector import containers, providers


class SimpleContainer(containers.DeclarativeContainer):
    """Simple container for testing dependency injection patterns."""

    config = providers.Configuration()

    # Simple service
    simple_service: providers.Singleton[str] = providers.Singleton(
        str,  # Using str as a simple service for testing
        "test-service",
    )


def test_simple_container() -> None:
    """Test that basic dependency injection works."""
    container = SimpleContainer()

    # Test configuration
    container.config.test_setting.from_value("test-value")
    assert container.config.test_setting() == "test-value"

    # Test service
    service = container.simple_service()
    assert service == "test-service"

    # Test singleton behavior
    service2 = container.simple_service()
    assert service is service2


def test_container_wiring() -> None:
    """Test that container wiring works."""
    container = SimpleContainer()

    # Should not raise an exception
    container.wire(modules=[__name__])

    # Test that the container is properly initialized
    assert container.simple_service() == "test-service"


if __name__ == "__main__":
    test_simple_container()
    test_container_wiring()
    print("✅ Basic dependency injection tests passed!")
