"""Main CLI entry point for the network security scanner."""

import sys
from pathlib import Path

import click
from rich.console import Console

from network_security_scanner.cli.commands.config import config_group
from network_security_scanner.cli.commands.report import report_group
from network_security_scanner.cli.commands.scan import scan_group
from network_security_scanner.cli.commands.validate import validate_group
from network_security_scanner.cli.options import common_options
from network_security_scanner.core.exceptions import NetworkScannerError

console = Console()


@click.group()
@click.version_option()
@common_options
@click.pass_context
def main(ctx: click.Context, verbose: bool, config_file: Path | None) -> None:
    """Network device configuration security analysis tool.

    This tool analyzes network device configurations for security
    vulnerabilities, compliance issues, and best practices violations.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config_file"] = config_file

    if verbose:
        console.print("[blue]Verbose mode enabled[/blue]")


# Add command groups
main.add_command(scan_group)
main.add_command(report_group)
main.add_command(validate_group)
main.add_command(config_group)


def cli_main() -> None:
    """Entry point for the CLI application."""
    try:
        main()
    except NetworkScannerError as e:
        console.print(f"[red]Error: {e}[/red]", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]", err=True)
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]", err=True)
        # Note: verbose mode exception printing would need context
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
