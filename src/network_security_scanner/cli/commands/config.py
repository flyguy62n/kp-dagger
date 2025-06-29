"""Configuration management CLI commands."""

import click


@click.group()
def config() -> None:
    """Configuration management commands."""


@config.command()
@click.option("--interactive", "-i", is_flag=True, help="Interactive configuration")
def init(*, interactive: bool) -> None:
    """Initialize application configuration."""
    _ = interactive  # Prevent unused variable warning
    click.echo("Initializing configuration...")


@config.command()
@click.argument("config_file", type=click.Path(exists=True))
def validate(config_file: str) -> None:
    """Validate configuration file."""
    _ = config_file  # Prevent unused variable warning
    click.echo("Validating configuration...")
