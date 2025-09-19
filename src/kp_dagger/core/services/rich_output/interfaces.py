"""Rich output interface protocols for dependency injection."""

from __future__ import annotations

from abc import abstractmethod
from contextlib import contextmanager
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Iterator

    from rich.tree import Tree


class MessageSeverity(StrEnum):
    """Standard severity levels for status messages."""

    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    DEBUG = "debug"


@runtime_checkable
class RichOutputProtocol(Protocol):
    """Protocol defining the Rich output interface for dependency injection."""

    @abstractmethod
    def success(self, message: str) -> None:
        """
        Display success message.

        Args:
            message: Success message to display

        """
        ...

    @abstractmethod
    def info(self, message: str) -> None:
        """
        Display informational message.

        Args:
            message: Info message to display

        """
        ...

    @abstractmethod
    def warning(self, message: str) -> None:
        """
        Display warning message.

        Args:
            message: Warning message to display

        """
        ...

    @abstractmethod
    def error(self, message: str) -> None:
        """
        Display error message to stderr.

        Args:
            message: Error message to display

        """
        ...

    @abstractmethod
    def critical(self, message: str) -> None:
        """
        Display critical error message to stderr.

        Args:
            message: Critical error message to display

        """
        ...

    @abstractmethod
    def debug(self, message: str) -> None:
        """
        Display debug message (only in verbose mode).

        Args:
            message: Debug message to display

        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    @contextmanager
    def progress(
        self,
        description: str = "Processing...",
        *,
        show_speed: bool = False,
        show_percentage: bool = True,
    ) -> Iterator[object]:
        """
        Context manager for progress tracking.

        Args:
            description: Description of the operation
            show_speed: Whether to show processing speed
            show_percentage: Whether to show percentage complete

        Yields:
            Progress object for task management

        """
        ...

    @abstractmethod
    @contextmanager
    def spinner(self, message: str = "Working...") -> Iterator[None]:
        """
        Context manager for simple spinner.

        Args:
            message: Message to display with spinner

        Yields:
            None

        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def file_error(self, file_path: str, error: str) -> None:
        """
        Display file-specific error.

        Args:
            file_path: Path to the file with error
            error: Error description

        """
        ...

    @abstractmethod
    def confirm_yes_no(self, question: str, *, default_yes: bool = True) -> bool:
        """
        Ask user for yes/no confirmation.

        Args:
            question: Question to ask the user
            default_yes: Whether default response is yes

        Returns:
            True if user confirms, False otherwise

        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def summary_panel(self, title: str, data: dict[str, object]) -> None:
        """
        Display summary information panel.

        Args:
            title: Panel title
            data: Key-value pairs to display

        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def tree(self, title: str) -> Tree:
        """
        Create a tree structure for display.

        Args:
            title: Tree root title

        Returns:
            Tree object for building hierarchy

        """
        ...

    @abstractmethod
    def print_tree(self, tree: Tree) -> None:
        """
        Print a tree structure.

        Args:
            tree: Tree object to display

        """
        ...

    @abstractmethod
    def print(self, message: str) -> None:
        """
        Print a generic message to stdout.

        Args:
            message: Message to display

        """
        ...

    @abstractmethod
    def print_code(self, code: str, *, lexer: str = "text") -> None:
        """
        Print syntax-highlighted code.

        Args:
            code: Code content to display
            lexer: Syntax highlighting language (e.g., "yaml", "json", "python")

        """
        ...
