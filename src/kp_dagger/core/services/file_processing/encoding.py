"""File encoding detection implementations for the file processing service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from charset_normalizer import CharsetMatch, from_path

if TYPE_CHECKING:
    from pathlib import Path


class CharsetNormalizerEncodingDetector:
    """Encoding detector using charset-normalizer for file processing."""

    def detect_encoding(self, file_path: Path) -> str | None:
        """
        Detect the encoding of a file using charset-normalizer.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected encoding name, or None if detection fails

        Raises:
            OSError: If file access errors occur
            Exception: If charset-normalizer fails

        """
        result: CharsetMatch | None = from_path(file_path).best()

        if result is not None:
            # Normalize encoding names for consistency
            encoding: str = result.encoding
            # Normalize underscore variants to hyphen variants for consistency
            # Both forms are valid in Python, but hyphens are more standard
            if encoding == "utf_8":
                encoding = "utf-8"
            elif encoding in {"iso_8859_1", "latin_1"}:
                encoding = "latin-1"
            # Note: We keep other encodings as-is since they're all valid
            # Examples: windows-1252, cp1252, ascii, etc.
            return encoding

        return None
