"""File validation implementation for path checking and access verification."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003


class BasicFileValidator:
    """
    Basic implementation of file validation operations.

    Provides methods to validate file and directory existence
    and accessibility.
    """

    def validate_file_exists(self, file_path: Path) -> bool:
        """
        Validate that a file exists and is accessible.

        Args:
            file_path: Path to validate

        Returns:
            True if the file exists and is a file, False otherwise

        """
        try:
            return file_path.exists() and file_path.is_file()
        except (OSError, PermissionError):
            return False

    def validate_directory_exists(self, dir_path: Path) -> bool:
        """
        Validate that a directory exists and is accessible.

        Args:
            dir_path: Path to validate

        Returns:
            True if the directory exists and is a directory, False otherwise

        """
        try:
            return dir_path.exists() and dir_path.is_dir()
        except (OSError, PermissionError):
            return False
