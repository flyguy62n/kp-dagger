"""Rich output service implementation for SSF Tools."""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import TYPE_CHECKING

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
from rich.theme import Theme
from rich.tree import Tree

from kp_dagger.core.services.rich_output.interfaces import MessageSeverity

if TYPE_CHECKING:
    from collections.abc import Iterator


class RichOutputService:
    """Rich output service implementing RichOutputProtocol for dependency injection."""

    # SSF Tools color theme
    SSF_THEME = Theme(
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
            theme=self.SSF_THEME,
            force_terminal=not no_color,
            width=width,
        )
        self.error_console = Console(
            stderr=True,
            theme=self.SSF_THEME,
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
                self.console.print(f"[success]✓[/success] {message}")

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
            self.console.print(f"[warning]⚠[/warning] {message}")

    def error(self, message: str) -> None:
        """
        Display error message to stderr.

        Args:
            message: Error message to display

        """
        with self._lock:
            self.error_console.print(f"[error]✗[/error] {message}")

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
        show_percentage: bool = True,
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
                f"[error]✗[/error] File error in [path]{file_path}[/path]: {error}",
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

    def results_table(
        self,
        data: list[dict[str, object]],
        columns: list[str],
        title: str | None = None,
    ) -> None:
        """
        Display results in table format.

        Args:
            data: List of row data
            columns: Column names to display
            title: Optional table title

        """
        if self.quiet or not data:
            return

        table = Table(title=title, show_header=True, header_style="bold blue")

        # Add columns
        for column in columns:
            table.add_column(column)

        # Add rows
        for row in data:
            table.add_row(*[str(row.get(col, "")) for col in columns])

        with self._lock:
            self.console.print(table)

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
