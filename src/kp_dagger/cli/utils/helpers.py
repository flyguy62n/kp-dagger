"""
Common utilities for PyBastion CLI.

Contains helper functions and utilities used across different CLI commands.
"""

import sys
from collections.abc import Sequence
from pathlib import Path

import click
from rich.console import Console

from kp_dagger.cli.utils.output import print_error

console = Console()


def validate_file_extensions(
    files: Sequence[Path],
    allowed_extensions: set[str],
) -> bool:
    """
    Validate that all files have allowed extensions.

    Args:
        files: List of file paths to validate
        allowed_extensions: Set of allowed file extensions (with dots)

    Returns:
        True if all files have valid extensions, False otherwise

    """
    invalid_files = []

    for file_path in files:
        if file_path.suffix.lower() not in allowed_extensions:
            invalid_files.append(file_path)

    if invalid_files:
        print_error("Invalid file extensions found:")
        for file_path in invalid_files:
            print_error(f"  {file_path} (extension: {file_path.suffix})")
        print_error(f"Allowed extensions: {', '.join(sorted(allowed_extensions))}")
        return False

    return True


def detect_device_type(config_file: Path) -> str:
    """
    Auto-detect device type from configuration file.

    Args:
        config_file: Path to the configuration file

    Returns:
        Detected device type string

    """
    max_read_lines = 50  # Limit to first 50 lines for performance
    try:
        with config_file.open("r", encoding="utf-8", errors="ignore") as f:
            # Read first few lines for detection
            content = ""
            for i, line in enumerate(f):
                content += line.lower()
                if i > max_read_lines:
                    break

        # Simple heuristics for device type detection
        if "version " in content and ("cisco" in content or "ios" in content):
            if "asa" in content or "pix" in content:
                return "cisco-asa"
            return "cisco-ios"
        if "config system global" in content or "fortigate" in content:
            return "fortigate"
        if "config" in content and ("paloalto" in content or "panorama" in content):
            return "paloalto"

    except (OSError, UnicodeDecodeError):
        return "cisco-ios"  # Safe default

    else:
        # Default fallback
        return "cisco-ios"


def get_output_filename(input_file: Path, suffix: str, extension: str) -> Path:
    """
    Generate an output filename based on input file.

    Args:
        input_file: Input file path
        suffix: Suffix to add to filename
        extension: New file extension

    Returns:
        Generated output file path

    """
    output_name = f"{input_file.stem}_{suffix}{extension}"
    return input_file.parent / output_name


def ensure_directory(path: Path) -> None:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists

    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print_error(f"Failed to create directory {path}: {e}")
        sys.exit(1)


def safe_file_write(file_path: Path, content: str, encoding: str = "utf-8") -> bool:
    """
    Safely write content to a file with error handling.

    Args:
        file_path: Path to write to
        content: Content to write
        encoding: File encoding

    Returns:
        True if successful, False otherwise

    """
    try:
        ensure_directory(file_path.parent)
        with file_path.open("w", encoding=encoding) as f:
            f.write(content)
    except OSError as e:
        print_error(f"Failed to write file {file_path}: {e}")
        return False
    return True


def get_file_size_human(file_path: Path) -> str:
    """
    Get human-readable file size.

    Args:
        file_path: Path to the file

    Returns:
        Human-readable size string

    """
    binary_divisor = 1024
    try:
        size = file_path.stat().st_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < binary_divisor:
                return f"{size:.1f} {unit}"
            size /= binary_divisor
    except OSError:
        return "Unknown"
    else:
        return f"{size:.1f} TB"


def is_binary_file(file_path: Path, chunk_size: int = 1024) -> bool:
    """
    Check if a file is binary by examining its content.

    Args:
        file_path: Path to the file to check
        chunk_size: Number of bytes to read for checking

    Returns:
        True if file appears to be binary, False otherwise

    """
    try:
        with file_path.open("rb") as f:
            chunk = f.read(chunk_size)

        # Check for null bytes (common in binary files)
        if b"\x00" in chunk:
            return True

        # Check if content is mostly printable ASCII
        try:
            chunk.decode("utf-8")
        except UnicodeDecodeError:
            return True
        else:
            # If we can decode it, assume it's text
            return False

    except OSError:
        return True  # Assume binary if we can't read it


class ClickAliasedGroup(click.Group):
    """Click group that supports command aliases."""

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        """Get command by name or alias."""
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        # Look for partial matches
        matches = [cmd for cmd in self.list_commands(ctx) if cmd.startswith(cmd_name)]
        if not matches:
            return None
        if len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])

        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")
        return None  # This line will never be reached, but satisfies type checker
