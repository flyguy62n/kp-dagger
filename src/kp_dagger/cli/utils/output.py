"""
Output utilities for PyBastion CLI.

Provides console utilities, logging configuration, and formatted output functions
using Rich for enhanced terminal experience.
"""

import logging
import sys
import types
from typing import Any, Self

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

__all__ = [
    "ProgressReporter",
    "RichCommand",
    "RichGroup",
    "confirm_action",
    "console",
    "error_console",
    "handle_keyboard_interrupt",
    "print_debug",
    "print_error",
    "print_info",
    "print_success",
    "print_warning",
    "setup_logging",
    "success_console",
]

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


def print_info(message: str, **kwargs: dict[str, Any]) -> None:
    """Print an info message."""
    console.print(f"ℹ️ {message}", style="info", **kwargs)  # noqa: RUF001


def print_warning(message: str, **kwargs: dict[str, Any]) -> None:
    """Print a warning message."""
    console.print(f"⚠️ {message}", style="warning", **kwargs)


def print_error(message: str, **kwargs: dict[str, Any]) -> None:
    """Print an error message."""
    error_console.print(f"❌ {message}", style="error", **kwargs)


def print_success(message: str, **kwargs: dict[str, Any]) -> None:
    """Print a success message."""
    success_console.print(f"✅ {message}", style="success", **kwargs)


def print_debug(message: str, **kwargs: dict[str, Any]) -> None:
    """Print a debug message."""
    console.print(f"🐛 {message}", style="debug", **kwargs)


def confirm_action(message: str, *, default: bool = False) -> bool:
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

    def __init__(self, description: str, console: Console | None = None) -> None:
        self.description = description
        self.console = console or globals()["console"]
        self.progress = None
        self.task = None

    def __enter__(self) -> Self:
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

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        if self.progress:
            self.progress.stop()

    def update(self, description: str) -> None:
        """Update the progress description."""
        if self.progress and self.task is not None:
            self.progress.update(self.task, description=description)


class RichGroup(click.Group):
    """
    Click Group with Rich-formatted help output.

    This class overrides Click's default help formatting to use Rich
    for enhanced terminal output with colors, styling, and better formatting.
    """

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:  # noqa: ARG002
        """Format the help page using Rich instead of Click's default formatter."""
        help_text = self.get_short_help_str()

        # Create Rich text object for the help content
        help_content = Text()

        # Add command name and description
        if self.name:
            help_content.append(f"{self.name}\n", style="bold blue")

        if help_text:
            help_content.append(f"{help_text}\n\n", style="")

        # Add usage section
        usage = self.get_usage(ctx)
        if usage:
            help_content.append("Usage:\n", style="bold yellow")
            help_content.append(f"  {usage}\n\n", style="dim")

        # Add options section
        if self.params:
            help_content.append("Options:\n", style="bold yellow")
            for param in self.params:
                if isinstance(param, click.Option):
                    opts = "/".join(param.opts)
                    help_line = f"  {opts:20} {param.help or ''}\n"
                    help_content.append(help_line, style="")
            help_content.append("\n")

        # Add commands section
        if hasattr(self, "commands") and self.commands:
            help_content.append("Commands:\n", style="bold yellow")
            for name, cmd in self.commands.items():
                cmd_help = cmd.get_short_help_str() or ""
                help_line = f"  {name:20} {cmd_help}\n"
                help_content.append(help_line, style="")

        # Display the formatted help
        panel = Panel(
            help_content,
            title="PyBastion CLI Help",
            border_style="blue",
            padding=(1, 2),
        )
        console.print(panel)


class RichCommand(click.Command):
    """
    Click Command with Rich-formatted help output.

    This class overrides Click's default help formatting to use Rich
    for enhanced terminal output.
    """

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:  # noqa: ARG002, C901, PLR0912
        """Format the help page using Rich instead of Click's default formatter."""
        help_text = self.help or "No help available."

        # Create Rich text object for the help content
        help_content = Text()

        # Add command name and description
        if self.name:
            help_content.append(f"{self.name}\n", style="bold blue")

        # Process help text to separate main description from examples
        lines = help_text.split("\n")
        main_help = []
        examples = []
        in_examples = False

        for line in lines:
            if line.strip().startswith("Examples:"):
                in_examples = True
            elif in_examples:
                examples.append(line)
            else:
                main_help.append(line)

        # Add main help text
        main_help_text = "\n".join(main_help).strip()
        if main_help_text:
            help_content.append(f"{main_help_text}\n\n", style="")

        # Add usage section
        usage = self.get_usage(ctx)
        if usage:
            help_content.append("Usage:\n", style="bold yellow")
            help_content.append(f"  {usage}\n\n", style="dim")

        # Separate arguments and options
        arguments = [p for p in self.params if isinstance(p, click.Argument)]
        options = [p for p in self.params if isinstance(p, click.Option)]

        # Add arguments section
        if arguments:
            help_content.append("Arguments:\n", style="bold yellow")
            for param in arguments:
                arg_name = param.name.upper()
                arg_desc = f"{param.name} argument"
                if param.required:
                    arg_desc += " (required)"
                help_line = f"  {arg_name:20} {arg_desc}\n"
                help_content.append(help_line, style="")
            help_content.append("\n")

        # Add options section
        if options:
            help_content.append("Options:\n", style="bold yellow")
            for param in options:
                opts = "/".join(param.opts)
                help_line = f"  {opts:20} {param.help or ''}\n"
                help_content.append(help_line, style="")
            help_content.append("\n")

        # Add examples section if present
        if examples:
            help_content.append("Examples:\n", style="bold yellow")
            for example in examples:
                if example.strip():
                    if example.strip().startswith("#"):
                        help_content.append(f"  {example}\n", style="dim cyan")
                    else:
                        help_content.append(f"  {example}\n", style="dim")

        # Display the formatted help
        panel = Panel(
            help_content,
            title=f"PyBastion - {self.name}",
            border_style="blue",
            padding=(1, 2),
        )
        console.print(panel)
