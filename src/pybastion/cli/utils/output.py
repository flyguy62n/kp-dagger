"""
Output utilities for PyBastion CLI.

Provides console utilities, logging configuration, and formatted output functions
using Rich for enhanced terminal experience.
"""

import logging
import sys
from typing import Any

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Custom theme for PyBastion CLI
PYBASTION_THEME = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "debug": "dim cyan",
        "highlight": "bold blue",
    },
)

# Console instances for different output types
console = Console(theme=PYBASTION_THEME)
error_console = Console(stderr=True, theme=PYBASTION_THEME, style="error")
success_console = Console(theme=PYBASTION_THEME, style="success")


def setup_logging(verbose: int = 0, quiet: bool = False) -> None:  # noqa: FBT001, FBT002
    """
    Setup logging configuration based on verbosity level.

    Args:
        verbose: Verbosity level (0=INFO, 1=DEBUG, 2+=TRACE)
        quiet: If True, suppress all output except errors

    """
    if quiet:
        log_level = logging.ERROR
    elif verbose == 0:
        log_level = logging.WARNING
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG

    # Configure rich handler
    rich_handler = RichHandler(
        console=console,
        show_time=verbose > 1,
        show_path=verbose > 1,
        markup=True,
        rich_tracebacks=True,
    )

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[rich_handler],
    )

    # Set logger for our package
    logger = logging.getLogger("pybastion")
    logger.setLevel(log_level)


def print_info(message: str, **kwargs: Any) -> None:
    """Print an info message."""
    console.print(f"ℹ️ {message}", style="info", **kwargs)


def print_warning(message: str, **kwargs: Any) -> None:
    """Print a warning message."""
    console.print(f"⚠️ {message}", style="warning", **kwargs)


def print_error(message: str, **kwargs: Any) -> None:
    """Print an error message."""
    error_console.print(f"❌ {message}", style="error", **kwargs)


def print_success(message: str, **kwargs: Any) -> None:
    """Print a success message."""
    success_console.print(f"✅ {message}", style="success", **kwargs)


def print_debug(message: str, **kwargs: Any) -> None:
    """Print a debug message."""
    console.print(f"🐛 {message}", style="debug", **kwargs)


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask for user confirmation.

    Args:
        message: Message to display
        default: Default value if user just presses Enter

    Returns:
        True if user confirms, False otherwise

    """
    default_str = "Y/n" if default else "y/N"
    response = console.input(f"❓ {message} [{default_str}]: ").strip().lower()

    if not response:
        return default

    return response in ("y", "yes", "true", "1")


def handle_keyboard_interrupt() -> None:
    """Handle Ctrl+C gracefully."""
    print_warning("Operation cancelled by user")
    sys.exit(130)  # Standard exit code for SIGINT


class ProgressReporter:
    """Context manager for reporting progress of long-running operations."""

    def __init__(self, description: str, console: Console | None = None):
        self.description = description
        self.console = console or globals()["console"]
        self.progress = None
        self.task = None

    def __enter__(self):
        from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console,
        )
        self.progress.start()
        self.task = self.progress.add_task(self.description, total=None)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.stop()

    def update(self, description: str) -> None:
        """Update the progress description."""
        if self.progress and self.task is not None:
            self.progress.update(self.task, description=description)
