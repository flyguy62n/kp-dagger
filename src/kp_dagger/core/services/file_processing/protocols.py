"""Protocol definitions for file processing service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from kp_dagger.models.base.types import PathLike


class EncodingDetector(Protocol):
    """Protocol for file encoding detection."""

    def detect_encoding(self, file_path: Path) -> str | None:
        """
        Detect the encoding of a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected encoding name, or None if detection fails

        """
        ...


class MimeTypeDetector(Protocol):
    """Protocol for MIME type detection."""

    def detect_mime_type(self, file_path: Path) -> str | None:
        """
        Detect the MIME type of a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected MIME type string, or None if detection fails

        """
        ...

    def is_text_file(self, file_path: Path) -> bool:
        """
        Check if a file is a text file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a text file, False otherwise

        """
        ...

    def is_binary_file(self, file_path: Path) -> bool:
        """
        Check if a file is a binary file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a binary file, False otherwise

        """
        ...


class HashGenerator(Protocol):
    """Protocol for file hash generation."""

    def generate_hash(self, file_path: Path) -> str:
        """
        Generate a hash for a file.

        Args:
            file_path: Path to the file to hash

        Returns:
            The generated hash as a hexadecimal string

        """
        ...


class FileValidator(Protocol):
    """Protocol for file validation."""

    def validate_file_exists(self, file_path: Path) -> bool:
        """
        Validate that a file exists and is accessible.

        Args:
            file_path: Path to validate

        Returns:
            True if the file exists and is a file, False otherwise

        """
        ...

    def validate_directory_exists(self, dir_path: Path) -> bool:
        """
        Validate that a directory exists and is accessible.

        Args:
            dir_path: Path to validate

        Returns:
            True if the directory exists and is a directory, False otherwise

        """
        ...


class FileDiscoverer(Protocol):
    """Protocol for discovering files in a directory."""

    def discover_files_by_pattern(
        self,
        base_path: PathLike,
        pattern: str = "*",
        *,
        recursive: bool = False,
    ) -> list[Path]:
        """
        Discover files matching a pattern in a directory.

        Args:
            base_path: Directory to search for files
            pattern: Glob pattern to match files
            recursive: If True, search subdirectories recursively (default: False)

        Returns:
            List of Path objects for all matching files

        """
        ...


class PathUtilities(Protocol):
    """Protocol for path utilities."""

    def generate_timestamped_path(
        self,
        base_path: PathLike,
        filename_prefix: str,
        extension: str,
    ) -> Path:
        """
        Generate a timestamped file path.

        Args:
            base_path: Base directory for the file
            filename_prefix: Prefix for the filename
            extension: File extension

        Returns:
            A Path object representing the generated file path

        """
        ...


class ContentStreamer(Protocol):
    """Protocol for streaming file content with targeted access patterns."""

    def get_file_header(self, lines: int = 10) -> list[str]:
        """
        Get the first N lines of the file.

        Args:
            lines: Number of lines to retrieve from the beginning

        Returns:
            List of strings, one per line

        """
        ...

    def stream_lines(self) -> Generator[str]:
        """
        Stream all lines in the file.

        Yields:
            All lines in the file, one at a time

        """
        ...


class FileProcessor(Protocol):
    """Service for all file processing operations."""

    def process_file(self, file_path: Path) -> dict[str, str | bool | None]:
        """
        Process a file and return metadata.

        Args:
            file_path: Path to the file to process

        Returns:
            Dictionary containing file metadata including encoding, hash, path,
            MIME type, and text/binary classification.
            Returns empty dict if file validation fails.

        """
        ...

    def detect_encoding(self, file_path: Path) -> str | None:
        """
        Detect the encoding of a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected encoding name, or None if detection fails

        """
        ...

    def generate_hash(self, file_path: Path) -> str:
        """
        Generate hash for a file.

        Args:
            file_path: Path to the file to hash

        Returns:
            The generated hash as a hexadecimal string

        """
        ...

    def detect_mime_type(self, file_path: Path) -> str | None:
        """
        Detect the MIME type of a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected MIME type string, or None if detection fails

        """
        ...

    def is_text_file(self, file_path: Path) -> bool:
        """
        Check if a file is a text file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a text file, False otherwise

        """
        ...

    def is_binary_file(self, file_path: Path) -> bool:
        """
        Check if a file is a binary file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a binary file, False otherwise

        """
        ...

    def discover_files_by_pattern(
        self,
        base_path: PathLike,
        pattern: str = "*",
        *,
        recursive: bool = False,
    ) -> list[Path]:
        """
        Discover files matching a pattern in a directory.

        Args:
            base_path: Directory to search for files
            pattern: Glob pattern to match files (default: "*")
            recursive: If True, search subdirectories recursively (default: False)

        Returns:
            List of Path objects for all matching files

        """
        ...

    def create_content_streamer(
        self,
        file_path: Path,
        encoding: str | None = None,
    ) -> ContentStreamer:
        """
        Create a content streamer for efficient file reading.

        Args:
            file_path: Path to the file to stream
            encoding: Character encoding (auto-detected if None)

        Returns:
            A ContentStreamer instance for the file

        Raises:
            ValueError: If encoding cannot be detected or file is invalid

        """
        ...
