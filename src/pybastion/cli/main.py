"""
Main CLI entry point for PyBastion.

This module provides the main command-line interface for PyBastion using Click.
It serves as the entry point for all CLI operations.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from pybastion.cli.commands.analyze import analyze
from pybastion.cli.commands.report import report
from pybastion.cli.commands.tenant import tenant
from pybastion.cli.utils.config import config
from pybastion.cli.utils.output import RichGroup, error_console, setup_logging

console = Console()


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
    "--config-file",
    type=click.Path(exists=True, path_type=str),
    help="Path to configuration file.",
)
@click.pass_context
def main(
    ctx: click.Context,
    version: bool,  # noqa: FBT001
    verbose: int,
    quiet: bool,  # noqa: FBT001
    output_format: str,
    config_file: str | None,
) -> None:
    """
    PyBastion - Network Device Configuration Security Analysis Tool.

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
    ctx.obj["config_file"] = config_file

    # Setup logging based on verbosity
    setup_logging(verbose, quiet)

    # NOTE: Container and DI integration will be added when all services are implemented
    # if config_file:
    #     try:
    #         from pybastion.containers.config import load_config
    #         from pybastion.containers import ApplicationContainer
    #
    #         config_data = load_config(config_file)
    #         container = ApplicationContainer()
    #         container.config.from_dict(config_data)
    #         container.wire_modules()
    #         ctx.obj["container"] = container
    #     except Exception as e:
    #         error_console.print(f"❌ Failed to load config: {e}", style="red")
    #         ctx.exit(1)

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
        from pybastion import __author__, __url__, __version__

        version_text = Text()
        version_text.append("PyBastion ", style="bold blue")
        version_text.append(f"v{__version__}", style="bold green")
        version_text.append(f"\nBy {__author__}", style="dim")
        version_text.append(f"\nWebsite: {__url__}", style="dim")

        panel = Panel(
            version_text,
            title="Version Information",
            border_style="blue",
            padding=(1, 2),
        )
        console.print(panel)

    except ImportError:
        error_console.print("❌ Could not determine version information", style="red")


def show_welcome() -> None:
    """Display welcome message."""
    welcome_text = Text()
    welcome_text.append("🏰 PyBastion\n", style="bold blue")
    welcome_text.append(
        "Network Device Configuration Security Analysis\n\n",
        style="blue",
    )
    welcome_text.append(
        "⚠️  Development Version - Not Production Ready",
        style="bold yellow",
    )

    panel = Panel(
        welcome_text,
        title="Welcome",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


# Add subcommands
main.add_command(analyze)
main.add_command(config)
main.add_command(report)
main.add_command(tenant)


if __name__ == "__main__":
    main()
