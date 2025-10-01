"""
Main CLI entry point for Dagger.

This module provides the main command-line interface for Dagger using Click.
It serves as the entry point for all CLI operations.
"""

import click
from dependency_injector.errors import Error as DIError
from pydantic import ValidationError

from kp_dagger.cli.utils.config import config
from kp_dagger.cli.utils.output import RichGroup, rich_output

# Configuration service
from kp_dagger.config import ConfigurationService

# Dependency Injection
from kp_dagger.containers.application import ApplicationContainer
from kp_dagger.core.exceptions import ConfigurationError

# Initialize global container
container = ApplicationContainer()

# Import commands after container initialization
from kp_dagger.cli.commands.analyze import analyze  # noqa: E402
from kp_dagger.cli.commands.report import report  # noqa: E402
from kp_dagger.cli.commands.tenant import tenant  # noqa: E402


@click.group(invoke_without_command=True, cls=RichGroup)
@click.option(
    "--version",
    is_flag=True,
    help="Show version information and exit.",
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity (can be used multiple times).",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress all output except errors.",
)
@click.option(
    "--output-format",
    type=click.Choice(["auto", "plain", "rich"], case_sensitive=False),
    default="auto",
    help="Output format for CLI messages.",
)
@click.option(
    "--config-dir",
    type=click.Path(exists=True, path_type=str),
    default="config",
    help="Path to configuration directory.",
)
@click.pass_context
def main(  # noqa: PLR0913
    ctx: click.Context,
    version: bool,  # noqa: FBT001
    verbose: int,
    quiet: bool,  # noqa: FBT001
    output_format: str,
    config_dir: str,
) -> None:
    """
    Dagger - Network Device Configuration Security Analysis Tool.

    A comprehensive tool for analyzing network device configurations for security
    vulnerabilities, compliance issues, and best practices violations.

    ⚠️  WARNING: This is a development version and is not ready for production use.
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)

    # Store global options in context
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["output_format"] = output_format
    ctx.obj["config_dir"] = config_dir

    # Initialize application configuration service
    try:
        config_service = ConfigurationService(config_dir=config_dir)
        ctx.obj["config_service"] = config_service
    except FileNotFoundError as e:
        rich_output.error(f"Configuration file not found: {e}")
        ctx.exit(1)
    except ValidationError as e:
        rich_output.error(f"Configuration validation failed: {e}")
        ctx.exit(1)
    except ConfigurationError as e:
        rich_output.error(f"Configuration service failed: {e}")
        ctx.exit(1)

    # Initialize and wire DI container (minimal config for compatibility)
    try:
        # Inject ConfigurationService into the container
        container.configuration_service.override(config_service)
        # Provide minimal configuration to prevent DI container errors
        # TEMPORARY: Minimal DI config until services use ConfigurationService
        minimal_di_config = {
            "core": {
                "database": {"path": ":memory:"},
                "encryption": {"master_key": "temp", "salt": "temp"},
            },
            "api_clients": {
                "cve": {"api_key": ""},
                "eol": {},
            },
            "scanner": {"verbose": verbose > 0},
        }
        container.config.from_dict(minimal_di_config)

        container.wire(
            modules=[
                "kp_dagger.cli.main",
                "kp_dagger.cli.commands.analyze",
                "kp_dagger.cli.commands.report",
                "kp_dagger.cli.commands.tenant",
            ],
        )
    except DIError as e:
        rich_output.error(f"Dependency injection error: {e}")
        ctx.exit(1)
    except ImportError as e:
        rich_output.error(f"Failed to import DI modules: {e}")
        ctx.exit(1)

    if version:
        show_version()
        ctx.exit()

    # If no command was provided, show help
    if ctx.invoked_subcommand is None:
        show_welcome()
        click.echo(ctx.get_help())


def show_version() -> None:
    """Display version information."""
    try:
        from kp_dagger import __author__, __url__, __version__

        version_data = {
            "Version": f"v{__version__}",
            "Author": __author__,
            "Website": __url__,
        }
        rich_output.summary_panel("Version Information", version_data)
    except ImportError:
        rich_output.error("Could not determine version information")


def show_welcome() -> None:
    """Display welcome message."""
    rich_output.info("🏰 [bold blue]Dagger[/bold blue]")
    rich_output.info("[blue]Network Device Configuration Security Analysis[/blue]")
    rich_output.warning("⚠️  Development Version - Not Production Ready")


# Add subcommands
main.add_command(analyze)
main.add_command(config)
main.add_command(report)
main.add_command(tenant)


if __name__ == "__main__":
    main()
