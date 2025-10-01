"""
Tenant command for Dagger CLI.

Handles tenant management including creation, deletion, and listing of tenants.
"""

import click

from kp_dagger.cli.utils.output import RichCommand, RichGroup, success_console


@click.group("tenant", cls=RichGroup)
def tenant() -> None:
    """
    Manage tenant configurations.

    ⚠️  WARNING: This is a development version and is not ready for production use.
    """


@tenant.command("create", cls=RichCommand)
@click.argument("name", type=str, required=True)
def create(name: str) -> None:
    """
    Create a new tenant configuration.

    ⚠️  WARNING: This is a development version and is not ready for production use.

    Examples:
        # Create a new tenant:
        Dagger tenant create "my-tenant"

    """
    success_console.print(f"✅ Created tenant configuration for: {name}")


@tenant.command("list", cls=RichCommand)
def list_tenants() -> None:
    """
    List all tenant configurations.

    ⚠️  WARNING: This is a development version and is not ready for production use.

    Examples:
        # List all tenants:
        Dagger tenant list

    """
    success_console.print("📋 Listing all tenant configurations...")
    # Implementation will be added later


@tenant.command("delete", cls=RichCommand)
@click.argument("name", type=str, required=True)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force deletion without confirmation.",
)
def delete(name: str, *, force: bool = False) -> None:
    """
    Delete a tenant configuration.

    ⚠️  WARNING: This is a development version and is not ready for production use.

    Examples:
        # Delete a tenant with confirmation:
        Dagger tenant delete "my-tenant"

        # Force delete without confirmation:
        Dagger tenant delete "my-tenant" --force

    """
    if not force and not click.confirm(
        f"Are you sure you want to delete tenant '{name}'?",
    ):
        success_console.print("❌ Deletion cancelled.")
        return

    success_console.print(f"🗑️  Deleted tenant configuration: {name}")
    # Implementation will be added later
