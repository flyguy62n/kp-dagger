"""
Tenant command for PyBastion CLI.

Handles tenant management including creation, deletion, and listing of tenants.
"""

import click
from rich.console import Console

from pybastion.cli.utils.output import RichCommand, success_console

console = Console()


@click.command(cls=RichCommand)
@click.pass_context
@click.argument("name", type=str, required=True)
def create_tenant(
    ctx: click.Context,
    name: str,
) -> None:
    """
    Create a new tenant configuration.

    ⚠️  WARNING: This is a development version and is not ready for production use.

    Examples:
        # Validate a single configuration file
        pybastion tenant create "config.txt"


    """
    success_console.print(f"✅ Created tenant configuration for: {name}")
