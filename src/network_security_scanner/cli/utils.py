"""CLI utility functions."""

import click


def echo_success(message: str) -> None:
    """Echo success message in green."""
    click.echo(click.style(message, fg="green"))


def echo_error(message: str) -> None:
    """Echo error message in red."""
    click.echo(click.style(message, fg="red"))


def echo_warning(message: str) -> None:
    """Echo warning message in yellow."""
    click.echo(click.style(message, fg="yellow"))


def echo_info(message: str) -> None:
    """Echo info message in blue."""
    click.echo(click.style(message, fg="blue"))
