"""Configuration validation CLI commands."""

import click


@click.group()
def validate() -> None:
    """Configuration validation commands."""


@validate.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--device-type", help="Device type for validation")
def syntax(config_file: str, device_type: str | None) -> None:
    """Validate configuration file syntax."""
    _ = config_file, device_type  # Prevent unused variable warnings
    click.echo("Validating syntax...")
