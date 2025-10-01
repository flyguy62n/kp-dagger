"""Main file processing service implementation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from kp_dagger.models.events import (
    OperationCompleted,
    OperationError,
    OperationStarted,
)

if TYPE_CHECKING:
    from kp_dagger.core.services.events import SafeEventPublisher
    from kp_dagger.core.services.file_processing.protocols import (
        ContentStreamer,
        EncodingDetector,
        FileDiscoverer,
        FileValidator,
        HashGenerator,
        MimeTypeDetector,
    )
    from kp_dagger.core.services.timestamp.protocols import TimestampProtocol
    from kp_dagger.models.base.types import PathLike


class FileProcessingService:
    """Service for all file processing operations."""

    def __init__(  # noqa: PLR0913
        self,
        encoding_detector: EncodingDetector,
        hash_generator: HashGenerator,
        file_validator: FileValidator,
        file_discovery: FileDiscoverer,
        mime_detector: MimeTypeDetector,
        event_publisher: SafeEventPublisher,
        timestamp_service: TimestampProtocol,
    ) -> None:
        """
        Initialize the file processing service.

        Args:
            encoding_detector: Service for detecting file encodings
            hash_generator: Service for generating file hashes
            file_validator: Service for validating file paths
            file_discovery: Service for finding files
            mime_detector: Service for detecting MIME types
            event_publisher: Service for publishing events to UI layer
            timestamp_service: Service for timestamp operations

        """
        self.encoding_detector: EncodingDetector = encoding_detector
        self.hash_generator: HashGenerator = hash_generator
        self.file_validator: FileValidator = file_validator
        self.file_discovery: FileDiscoverer = file_discovery
        self.mime_detector: MimeTypeDetector = mime_detector
        self.event_publisher: SafeEventPublisher = event_publisher
        self.timestamp_service: TimestampProtocol = timestamp_service

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
        start_time = self.timestamp_service.utc_now()

        # Publish operation started event
        self.event_publisher.publish(
            OperationStarted(
                operation_type="file_processing",
                resource_path=file_path,
                display_name=file_path.name,
                context={"operation": "metadata_extraction"},
            ),
        )

        try:
            if not self.file_validator.validate_file_exists(file_path):
                self.event_publisher.publish(
                    OperationError(
                        operation_type="file_processing",
                        resource_path=file_path,
                        display_name=file_path.name,
                        error_message=f"File not found: {file_path}",
                        error_context={"operation": "file_validation"},
                    ),
                )
                return {}

            encoding: str | None = self.encoding_detector.detect_encoding(file_path)
            if encoding is None:
                self.event_publisher.publish(
                    OperationError(
                        operation_type="file_processing",
                        resource_path=file_path,
                        error_message=f"Could not detect encoding for: {file_path}",
                        error_context={"operation": "encoding_detection"},
                    ),
                )
                return {}

            file_hash: str = self.hash_generator.generate_hash(file_path)

            # Get MIME type information
            mime_type: str | None = self.mime_detector.detect_mime_type(file_path)
            is_text: bool = self.mime_detector.is_text_file(file_path)

            result = {
                "encoding": encoding,
                "hash": file_hash,
                "path": str(file_path),
                "mime_type": mime_type,
                "is_text": is_text,
            }

            # Publish successful completion
            duration = self.timestamp_service.elapsed_seconds(start_time)
            self.event_publisher.publish(
                OperationCompleted(
                    operation_type="file_processing",
                    resource_path=file_path,
                    display_name=file_path.name,
                    success=True,
                    duration=duration,
                    results={
                        "metadata_extracted": True,
                        "encoding": encoding,
                        "mime_type": mime_type,
                        "is_text": is_text,
                    },
                ),
            )

        except (OSError, ValueError, RuntimeError) as e:
            # Publish error event for unexpected failures
            duration = self.timestamp_service.elapsed_seconds(start_time)
            self.event_publisher.publish(
                OperationError(
                    operation_type="file_processing",
                    resource_path=file_path,
                    display_name=file_path.name,
                    error_message=str(e),
                    error_context={
                        "operation": "metadata_extraction",
                        "duration": duration,
                    },
                ),
            )
            return {}
        else:
            return result

    def detect_encoding(self, file_path: Path) -> str | None:
        """
        Detect the encoding of a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected encoding name, or None if detection fails

        """
        return self.encoding_detector.detect_encoding(file_path)

    def generate_hash(self, file_path: Path) -> str:
        """
        Generate hash for a file.

        Args:
            file_path: Path to the file to hash

        Returns:
            The generated hash as a hexadecimal string

        """
        return self.hash_generator.generate_hash(file_path)

    def detect_mime_type(self, file_path: Path) -> str | None:
        """
        Detect the MIME type of a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected MIME type string, or None if detection fails

        """
        return self.mime_detector.detect_mime_type(file_path)

    def is_text_file(self, file_path: Path) -> bool:
        """
        Check if a file is a text file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a text file, False otherwise

        """
        return self.mime_detector.is_text_file(file_path)

    def is_binary_file(self, file_path: Path) -> bool:
        """
        Check if a file is a binary file based on its MIME type.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file is detected as a binary file, False otherwise

        """
        return self.mime_detector.is_binary_file(file_path)

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
        start_time = self.timestamp_service.utc_now()
        base_path_obj = Path(base_path)

        # Publish operation started event
        self.event_publisher.publish(
            OperationStarted(
                operation_type="file_discovery",
                resource_path=base_path_obj,
                display_name=base_path_obj.name or str(base_path_obj),
                context={"pattern": pattern, "recursive": recursive},
            ),
        )

        try:
            results = self.file_discovery.discover_files_by_pattern(
                base_path,
                pattern,
                recursive=recursive,
            )

            # Publish successful completion
            duration = self.timestamp_service.elapsed_seconds(start_time)
            self.event_publisher.publish(
                OperationCompleted(
                    operation_type="file_discovery",
                    resource_path=base_path_obj,
                    display_name=base_path_obj.name or str(base_path_obj),
                    success=True,
                    duration=duration,
                    results={
                        "files_found": len(results),
                        "pattern": pattern,
                        "recursive": recursive,
                    },
                ),
            )

        except (OSError, ValueError) as e:
            # Publish error event for discovery failures
            duration = self.timestamp_service.elapsed_seconds(start_time)
            self.event_publisher.publish(
                OperationError(
                    operation_type="file_discovery",
                    resource_path=base_path_obj,
                    display_name=base_path_obj.name or str(base_path_obj),
                    error_message=str(e),
                    error_context={
                        "pattern": pattern,
                        "recursive": recursive,
                        "duration": duration,
                    },
                ),
            )
            return []
        else:
            return results

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
        # Import here to avoid circular import
        from kp_dagger.core.services.file_processing.streaming import (
            FileContentStreamer,
        )

        # Validate file exists
        if not self.file_validator.validate_file_exists(file_path):
            msg = f"File does not exist: {file_path}"
            raise ValueError(msg)

        # Auto-detect encoding if not provided
        if encoding is None:
            encoding = self.encoding_detector.detect_encoding(file_path)
            if encoding is None:
                msg = f"Could not detect encoding for file: {file_path}"
                raise ValueError(msg)

        return FileContentStreamer(file_path, encoding)
