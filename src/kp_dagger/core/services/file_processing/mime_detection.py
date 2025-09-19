"""MIME type detection service using python-magic library."""

from __future__ import annotations

from typing import TYPE_CHECKING

import magic

if TYPE_CHECKING:
    from pathlib import Path

from kp_dagger.core.services.file_processing.protocols import MimeTypeDetector


class MimeDetector(MimeTypeDetector):
    """MIME type detector using python-magic library."""

    def __init__(self) -> None:
        """Initialize the MIME type detector."""
        self._magic_mime = magic.Magic(mime=True)

    def detect_mime_type(self, file_path: Path) -> str | None:
        """
        Detect the MIME type of a file using python-magic.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected MIME type string, or None if detection fails

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read

        """
        if not file_path.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

        if not file_path.is_file():
            return None

        # Handle empty files gracefully
        if file_path.stat().st_size == 0:
            return "application/x-empty"

        try:
            mime_type = self._magic_mime.from_file(str(file_path))
            return str(mime_type) if mime_type else None
        except (OSError, magic.MagicException):
            # Return None on any magic detection failure
            return None

    def is_text_file(self, file_path: Path) -> bool:
        """
        Check if a file is a text file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a text file, False otherwise

        """
        try:
            mime_type = self.detect_mime_type(file_path)
            if not mime_type:
                return False

            # Common text MIME types
            text_mime_prefixes = [
                "text/",
                "application/json",
                "application/xml",
                "application/yaml",
                "application/toml",
                "application/javascript",
                "application/x-sh",
                "application/x-shellscript",
            ]

            # Additional specific text types
            text_mime_types = {
                "application/x-empty",  # Empty files
                "inode/x-empty",  # Empty files (alternative)
            }

            mime_lower = mime_type.lower()

            return (
                any(mime_lower.startswith(prefix) for prefix in text_mime_prefixes)
                or mime_lower in text_mime_types
            )

        except (FileNotFoundError, PermissionError):
            return False

    def is_binary_file(self, file_path: Path) -> bool:
        """
        Check if a file is a binary file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a binary file, False otherwise

        """
        try:
            mime_type = self.detect_mime_type(file_path)
            if not mime_type:
                # If we can't detect the MIME type, assume it's binary for safety
                return True

            # If it's a text file, it's not binary
            return not self.is_text_file(file_path)

        except (FileNotFoundError, PermissionError):
            return False
