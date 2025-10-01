"""
Rich output utilities for Dagger CLI.

Provides Rich-based console utilities and formatted output functions
for enhanced terminal experience using the event-driven architecture.
"""

from __future__ import annotations

import sys
import threading
from contextlib import contextmanager
from enum import StrEnum
from typing import TYPE_CHECKING, Self, cast

if TYPE_CHECKING:
    import types
    from collections.abc import Iterator, Mapping, Sequence

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Confirm, Prompt
from rich.status import Status
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich.tree import Tree

if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = [
    "MessageSeverity",
    "RichCommand",
    "RichGroup",
    "RichOutputService",
    "console",
    "error_console",
    "handle_keyboard_interrupt",
    "print_debug",
    "print_error",
    "print_info",
    "print_success",
    "print_warning",
    "rich_output",
    "success_console",
]


class MessageSeverity(StrEnum):
    """Standard severity levels for status messages."""

    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    DEBUG = "debug"


class RichOutputService:
    """Rich output service for CLI user interface."""

    # Dagger CLI color theme
    DAGGER_THEME = Theme(
        {
            "success": "bold green",
            "info": "cyan",
            "warning": "bold yellow",
            "error": "bold red",
            "critical": "bold white on red",
            "debug": "dim white",
            "highlight": "bold magenta",
            "path": "blue",
            "value": "green",
            "key": "yellow",
            "panel.border": "blue",
            "panel.title": "bold blue",
        },
    )

    def __init__(
        self,
        *,
        quiet: bool = False,
        verbose: bool = False,
        no_color: bool = False,
        width: int | None = None,
    ) -> None:
        """
        Initialize Rich output interface.

        Args:
            quiet: Suppress non-essential output
            verbose: Show debug and detailed messages
            no_color: Disable color output
            width: Force console width

        """
        self.quiet = quiet
        self.verbose = verbose

        # Create consoles with appropriate settings
        self.console = Console(
            theme=self.DAGGER_THEME,
            force_terminal=not no_color,
            width=width,
        )
        self.error_console = Console(
            stderr=True,
            theme=self.DAGGER_THEME,
            force_terminal=not no_color,
            width=width,
        )

        # Thread safety for concurrent operations
        self._lock = threading.Lock()

    def success(self, message: str) -> None:
        """
        Display success message.

        Args:
            message: Success message to display

        """
        if not self.quiet:
            with self._lock:
                self.console.print(f"[success]✅[/success] {message}")

    def info(self, message: str) -> None:
        """
        Display informational message.

        Args:
            message: Info message to display

        """
        if not self.quiet:
            with self._lock:
                self.console.print(f"[info]i[/info] {message}")

    def warning(self, message: str) -> None:
        """
        Display warning message.

        Args:
            message: Warning message to display

        """
        with self._lock:
            self.console.print(f"[warning]⚠️[/warning] {message}")

    def error(self, message: str) -> None:
        """
        Display error message to stderr.

        Args:
            message: Error message to display

        """
        with self._lock:
            self.error_console.print(f"[error]❌[/error] {message}")

    def critical(self, message: str) -> None:
        """
        Display critical error message to stderr.

        Args:
            message: Critical error message to display

        """
        with self._lock:
            self.error_console.print(f"[critical]💀 CRITICAL:[/critical] {message}")

    def debug(self, message: str) -> None:
        """
        Display debug message (only in verbose mode).

        Args:
            message: Debug message to display

        """
        if self.verbose:
            with self._lock:
                self.console.print(f"[debug]🐛 DEBUG:[/debug] {message}")

    def status(
        self,
        message: str,
        severity: MessageSeverity = MessageSeverity.INFO,
    ) -> None:
        """
        Display status message with appropriate severity.

        Args:
            message: Status message to display
            severity: Message severity level

        """
        severity_methods = {
            MessageSeverity.SUCCESS: self.success,
            MessageSeverity.INFO: self.info,
            MessageSeverity.WARNING: self.warning,
            MessageSeverity.ERROR: self.error,
            MessageSeverity.CRITICAL: self.critical,
            MessageSeverity.DEBUG: self.debug,
        }

        method = severity_methods.get(severity, self.info)
        method(message)

    @contextmanager
    def progress(
        self,
        description: str = "Processing...",
        *,
        show_speed: bool = False,
        show_percentage: bool = False,
    ) -> Iterator[Progress]:
        """
        Context manager for progress tracking.

        Args:
            description: Description of the operation
            show_speed: Whether to show processing speed
            show_percentage: Whether to show percentage complete

        Yields:
            Progress object for task management

        """
        if self.quiet:
            # Minimal progress in quiet mode
            yield None  # type: ignore[misc]
            return

        columns = [
            SpinnerColumn(),
            TextColumn(f"[progress.description]{description}"),
        ]

        if show_percentage:
            columns.append(BarColumn())
            columns.append(TextColumn("[progress.percentage]{task.percentage:>3.0f}%"))

        if show_speed:
            columns.append(TextColumn("[progress.data.speed]{task.speed}"))

        columns.append(TimeElapsedColumn())

        with Progress(*columns, console=self.console) as progress:
            yield progress

    @contextmanager
    def spinner(self, message: str = "Working...") -> Iterator[None]:
        """
        Context manager for simple spinner.

        Args:
            message: Message to display with spinner

        Yields:
            None

        """
        if self.quiet:
            yield
            return

        with Status(message, console=self.console):
            yield

    def error_panel(
        self,
        error: Exception,
        context: dict[str, object] | None = None,
    ) -> None:
        """
        Display detailed error information.

        Args:
            error: Exception to display
            context: Additional context information

        """
        error_content = [f"[error]{type(error).__name__}:[/error] {error}"]

        if context:
            error_content.append("")
            error_content.append("[key]Context:[/key]")
            for key, value in context.items():
                error_content.append(f"  [key]{key}:[/key] [value]{value}[/value]")

        panel = Panel(
            "\n".join(error_content),
            title="[error]Error Details[/error]",
            border_style="red",
        )

        with self._lock:
            self.error_console.print(panel)

    def file_error(self, file_path: str, error: str) -> None:
        """
        Display file-specific error.

        Args:
            file_path: Path to the file with error
            error: Error description

        """
        with self._lock:
            self.error_console.print(
                f"[error]❌[/error] File error in [path]{file_path}[/path]: {error}",
            )

    def confirm_yes_no(self, question: str, *, default_yes: bool = True) -> bool:
        """
        Ask user for yes/no confirmation.

        Args:
            question: Question to ask the user
            default_yes: Whether default response is yes

        Returns:
            True if user confirms, False otherwise

        """
        with self._lock:
            return Confirm.ask(question, default=default_yes, console=self.console)

    def prompt(
        self,
        question: str,
        default: str | None = None,
        choices: list[str] | None = None,
    ) -> str:
        """
        Prompt user for input.

        Args:
            question: Question to ask the user
            default: Default value if user just presses enter
            choices: List of valid choices (for validation)

        Returns:
            User's input as string

        """
        with self._lock:
            result = Prompt.ask(
                question,
                default=default,
                choices=choices,
                console=self.console,
            )
            return result or ""

    def summary_panel(self, title: str, data: dict[str, object]) -> None:
        """
        Display summary information panel.

        Args:
            title: Panel title
            data: Key-value pairs to display

        """
        if self.quiet:
            return

        content_lines = []
        for key, value in data.items():
            content_lines.append(f"[key]{key}:[/key] [value]{value}[/value]")

        panel = Panel(
            "\n".join(content_lines),
            title=f"[panel.title]{title}[/panel.title]",
            border_style="blue",
        )

        with self._lock:
            self.console.print(panel)

    def _create_dict_table(
        self,
        data: Mapping[str, object],
        title: str | None,
        show_header: bool,
        column_styles: dict[str, str] | None,
    ) -> Table:
        """Create a two-column key-value table from dict data."""
        rich_table = Table(title=title, show_header=show_header)

        # Use theme-aware default styles for key-value tables
        key_style = column_styles.get("key", "cyan") if column_styles else "cyan"
        value_style = column_styles.get("value", "white") if column_styles else "white"

        rich_table.add_column("Setting", style=key_style)
        rich_table.add_column("Value", style=value_style)

        for key, value in data.items():
            # Format boolean values
            if isinstance(value, bool):
                display_value = "Yes" if value else "No"
            else:
                display_value = str(value)
            rich_table.add_row(key, display_value)

        return rich_table

    def _create_sequence_table(
        self,
        data: Sequence[Mapping[str, object]],
        columns: list[str],
        title: str | None,
        show_header: bool,
        header_style: str,
        column_styles: dict[str, str] | None,
    ) -> Table:
        """Create a multi-column table from sequence data."""
        rich_table = Table(
            title=title,
            show_header=show_header,
            header_style=header_style,
        )

        # Add columns with optional per-column styling
        for column in columns:
            col_style = column_styles.get(column) if column_styles else None
            rich_table.add_column(column, style=col_style)

        # Add rows
        for row in data:
            rich_table.add_row(*[str(row.get(col, "")) for col in columns])

        return rich_table

    def table(
        self,
        data: Mapping[str, object] | Sequence[Mapping[str, object]],
        columns: list[str] | None = None,
        *,
        title: str | None = None,
        show_header: bool | None = None,
        header_style: str = "bold blue",
        column_styles: dict[str, str] | None = None,
    ) -> None:
        """
        Display data in table format.

        Handles two display modes:
        1. Dict mode: Two-column key-value table (when data is a dict)
        2. Multi-column mode: N-column tabular data (when data is a sequence)

        Args:
            data: Either a Mapping for key-value display or sequence of Mappings for tabular data
            columns: Column names (required for sequence data, ignored for dict data)
            title: Optional table title
            show_header: Whether to show column headers (auto-detected if None)
            header_style: Style for header row
            column_styles: Per-column styles as {column_name: style_string}

        Raises:
            ValueError: If sequence data provided without columns parameter

        Examples:
            # Key-value configuration display
            rich_output.table({"Setting": "value", "Enable": True}, title="Config")

            # Multi-column results display
            rich_output.table(
                [{"Name": "Alice", "Score": 95}, {"Name": "Bob", "Score": 87}],
                columns=["Name", "Score"],
                title="Results"
            )

        """
        if self.quiet:
            return

        # Handle dict mode (key-value pairs)
        if isinstance(data, dict):
            if show_header is None:
                show_header = False
            rich_table = self._create_dict_table(
                data,
                title,
                show_header,
                column_styles,
            )

        # Handle sequence mode (multi-column tabular data)
        else:
            if not data:
                return

            if columns is None:
                msg = "columns parameter is required when data is a sequence"
                raise ValueError(msg)

            if show_header is None:
                show_header = True

            # Type narrowing: data must be Sequence at this point
            rich_table = self._create_sequence_table(
                cast("Sequence[Mapping[str, object]]", data),
                columns,
                title,
                show_header,
                header_style,
                column_styles,
            )

        with self._lock:
            self.console.print(rich_table)

    def tree(self, title: str) -> Tree:
        """
        Create a tree structure for display.

        Args:
            title: Tree root title

        Returns:
            Tree object for building hierarchy

        """
        return Tree(title)

    def print_tree(self, tree: Tree) -> None:
        """
        Print a tree structure.

        Args:
            tree: Tree object to display

        """
        if not self.quiet:
            with self._lock:
                self.console.print(tree)

    def print(self, message: str) -> None:
        """
        Print a generic message to stdout.

        Args:
            message: Message to display

        """
        if not self.quiet:
            with self._lock:
                self.console.print(message)

    def print_code(self, code: str, *, lexer: str = "text") -> None:
        """
        Print syntax-highlighted code.

        Args:
            code: Code content to display
            lexer: Syntax highlighting language (e.g., "yaml", "json", "python")

        """
        if not self.quiet:
            with self._lock:
                from rich.syntax import Syntax

                syntax = Syntax(code, lexer, theme="monokai", line_numbers=False)
                self.console.print(syntax)


def handle_keyboard_interrupt() -> None:
    """Handle Ctrl+C gracefully."""
    rich_output.warning("Operation cancelled by user")
    sys.exit(130)  # Standard exit code for SIGINT


class ProgressReporter:
    """Context manager for reporting progress of long-running operations."""

    def __init__(self, description: str, console: Console | None = None) -> None:
        self.description = description
        self.console = console or rich_output.console
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
            title="Dagger CLI Help",
            border_style="blue",
            padding=(1, 2),
        )
        rich_output.console.print(panel)


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
                arg_name = (param.name or "").upper()
                arg_desc = f"{param.name or 'argument'} argument"
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
            title=f"Dagger - {self.name}",
            border_style="blue",
            padding=(1, 2),
        )
        rich_output.console.print(panel)


# Global instances - can be configured by CLI based on verbosity/quiet settings
rich_output = RichOutputService()

# Backward compatibility console instances
console = rich_output.console
error_console = rich_output.error_console
success_console = rich_output.console


# Backward compatibility functions
def print_info(message: str) -> None:
    """Print an info message."""
    rich_output.info(message)


def print_warning(message: str) -> None:
    """Print a warning message."""
    rich_output.warning(message)


def print_error(message: str) -> None:
    """Print an error message."""
    rich_output.error(message)


def print_success(message: str) -> None:
    """Print a success message."""
    rich_output.success(message)


def print_debug(message: str) -> None:
    """Print a debug message."""
    rich_output.debug(message)
