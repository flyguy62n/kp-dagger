"""
Configuration utilities for Dagger CLI.

Handles configuration file loading, validation, and management for the CLI interface.
"""

import json
from pathlib import Path
from typing import Any, ClassVar

import click
from rich.console import Console

from kp_dagger.cli.utils.output import print_error, print_info

console = Console()


class ConfigManager:
    """Manages CLI configuration settings."""

    DEFAULT_CONFIG: ClassVar[dict[str, Any]] = {
        "output_format": "table",
        "verbose": 0,
        "parallel_jobs": 1,
        "default_device_type": "auto",
        "include_passed_checks": False,
        "severity_filter": "all",
        "report_template": "default",
    }

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize configuration manager."""
        self.config_path = config_path or self._get_default_config_path()
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()

    def _get_default_config_path(self) -> Path:
        """Get the default configuration file path."""
        # Use user's home directory for config
        config_dir = Path.home() / ".Dagger"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.json"

    def load(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            print_info(
                f"No configuration file found at {self.config_path}, using defaults",
            )
            return

        try:
            with self.config_path.open("r", encoding="utf-8") as f:
                user_config = json.load(f)

            # Merge with defaults
            self.config.update(user_config)
            print_info(f"Loaded configuration from {self.config_path}")

        except (json.JSONDecodeError, OSError) as e:
            print_error(f"Failed to load configuration: {e}")
            print_info("Using default configuration")

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with self.config_path.open("w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            print_info(f"Configuration saved to {self.config_path}")
        except OSError as e:
            print_error(f"Failed to save configuration: {e}")

    def get(
        self,
        key: str,
        default: dict[str, Any] | None = None,
    ) -> str | float | bool | dict[str, Any]:
        """Get a configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: str | float | bool | dict[str, Any]) -> None:
        """Set a configuration value."""
        self.config[key] = value

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.config: dict[str, Any] = self.DEFAULT_CONFIG.copy()

    def show(self) -> None:
        """Display current configuration."""
        from rich.table import Table

        table = Table(title="Dagger Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        for key, value in sorted(self.config.items()):
            table.add_row(key, str(value))

        console.print(table)


@click.command()
@click.option(
    "--show",
    is_flag=True,
    help="Show current configuration.",
)
@click.option(
    "--reset",
    is_flag=True,
    help="Reset configuration to defaults.",
)
@click.option(
    "--set",
    "set_option",
    nargs=2,
    multiple=True,
    metavar="KEY VALUE",
    help="Set configuration option (can be used multiple times).",
)
@click.pass_context
def config(
    ctx: click.Context,  # noqa: ARG001
    *,
    show: bool,
    reset: bool,
    set_option: tuple[tuple[str, str], ...],
) -> None:
    """
    Manage Dagger CLI configuration.

    ⚠️  WARNING: This is a development version and is not ready for production use.

    Examples:
        # Show current configuration
        Dagger config --show

        # Set default output format
        Dagger config --set output_format json

        # Reset to defaults
        Dagger config --reset

    """
    config_manager = ConfigManager()

    if reset:
        config_manager.reset()
        config_manager.save()
        print_info("Configuration reset to defaults")
        return

    if set_option:
        for key, _value in set_option:
            # Try to convert to appropriate type
            if _value.lower() in ("true", "false"):
                value = _value.lower() == "true"
            elif _value.isdigit():
                value = int(value)

            config_manager.set(key, value)

        config_manager.save()
        print_info(f"Updated {len(set_option)} configuration option(s)")

    if show or not (reset or set_option):
        config_manager.show()
