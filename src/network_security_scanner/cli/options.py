"""Common CLI options and decorators."""

from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

import click


def common_options(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for common CLI options."""

    @click.option(
        "--config-file",
        "-c",
        type=click.Path(exists=True, path_type=Path),
        help="Configuration file path",
    )
    @click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper


def database_options(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for database-related options."""

    @click.option(
        "--database", "-d", type=click.Path(path_type=Path), help="Database file path"
    )
    @click.option("--memory", is_flag=True, help="Use in-memory database")
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper


def output_options(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for output-related options."""

    @click.option(
        "--output", "-o", type=click.Path(path_type=Path), help="Output file path"
    )
    @click.option(
        "--format",
        "output_format",
        type=click.Choice(["json", "html", "excel"], case_sensitive=False),
        default="json",
        help="Output format",
    )
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper


# Common Click parameter types
DeviceTypeChoice = click.Choice(["cisco-ios", "cisco-asa", "fortigate", "paloalto"])
ReportFormatChoice = click.Choice(["json", "html", "excel"])
SeverityChoice = click.Choice(["low", "medium", "high", "critical"])
