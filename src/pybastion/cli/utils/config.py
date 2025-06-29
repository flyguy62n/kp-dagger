"""
Configuration utilities for PyBastion CLI.

Handles configuration file loading, validation, and management for the CLI interface.
"""

import json
from pathlib import Path
from typing import Any

import click
from rich.console import Console

from pybastion.cli.utils.output import print_error, print_info

console = Console()


class ConfigManager:
    """Manages CLI configuration settings."""

    DEFAULT_CONFIG = {
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
        config_dir = Path.home() / ".pybastion"
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

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config[key] = value

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()

    def show(self) -> None:
        """Display current configuration."""
        from rich.table import Table

        table = Table(title="PyBastion Configuration")
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
    ctx: click.Context,
    show: bool,
    reset: bool,
    set_option: tuple[tuple[str, str], ...],
) -> None:
    """
    Manage PyBastion CLI configuration.

    ⚠️  WARNING: This is a development version and is not ready for production use.

    Examples:
        # Show current configuration
        pybastion config --show

        # Set default output format
        pybastion config --set output_format json

        # Reset to defaults
        pybastion config --reset

    """
    config_manager = ConfigManager()

    if reset:
        config_manager.reset()
        config_manager.save()
        print_info("Configuration reset to defaults")
        return

    if set_option:
        for key, value in set_option:
            # Try to convert to appropriate type
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)

            config_manager.set(key, value)

        config_manager.save()
        print_info(f"Updated {len(set_option)} configuration option(s)")

    if show or not (reset or set_option):
        config_manager.show()
