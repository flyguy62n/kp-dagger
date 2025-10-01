"""
FortiGate configuration parser.

Uses common value cleaning utilities that provide:
- IPv6 address detection and preservation across all network device parsers
- Consistent boolean value handling (enable/disable, true/false, etc.)
- IP address preservation (both IPv4 and IPv6)
- Numeric conversion with proper type hints
- Quote removal standardization

These utilities will be shared with Cisco ASA, Cisco IOS, SonicWall, and other parsers.
"""

import re
from pathlib import Path
from typing import Any

from kp_dagger.core.exceptions import UnrecognizedLineFormatError
from kp_dagger.core.services.events import SafeEventPublisher
from kp_dagger.core.services.file_processing import FileProcessor
from kp_dagger.core.services.timestamp import TimestampService
from kp_dagger.models.base.types import PathLike
from kp_dagger.models.events import (
    OperationCompleted,
    OperationError,
    OperationStarted,
)
from kp_dagger.parsers.common.value_cleaners import FortigateCleaner


class FortigateConfigParser:
    """
    Stateless FortiGate configuration parser using stacks and regex.

    This approach trades grammar formalism for implementation simplicity.
    Each parse operation maintains its own state and does not affect the parser instance.
    """

    def __init__(
        self,
        file_processing_service: FileProcessor,
        event_publisher: SafeEventPublisher,
        timestamp_service: TimestampService,
        value_cleaner: FortigateCleaner,
    ) -> None:
        self.event_publisher: SafeEventPublisher = event_publisher
        self.file_processing_service: FileProcessor = file_processing_service
        self.timestamp_service: TimestampService = timestamp_service
        self.value_cleaner: FortigateCleaner = value_cleaner

        # Regex patterns for different line types (immutable)
        self.patterns = {
            "config": re.compile(r"^\s*config\s+(.+)$"),
            "edit": re.compile(r'^\s*edit\s+"?([^"]+)"?\s*$'),
            "set": re.compile(r"^\s*set\s+(\S+)\s+(.+)$"),
            "unset": re.compile(r"^\s*unset\s+(\S+)$"),
            "next": re.compile(r"^\s*next\s*$"),
            "end": re.compile(r"^\s*end\s*$"),
            "config_version": re.compile(r"^\s*#config-version=([^:]+):(.*)"),
            "comment": re.compile(r"^\s*#.*$"),
            "empty": re.compile(r"^\s*$"),
        }

    def parse_file(self, file_path: PathLike) -> dict[str, Any]:
        """Parse a FortiGate configuration file."""
        # Convert to Path object if needed
        if not isinstance(file_path, Path):
            try:
                file_path = Path(file_path)
            except (TypeError, ValueError) as e:
                self.event_publisher.publish(
                    OperationError(
                        operation_type="parsing",
                        resource_path=None,
                        error_message=f"Invalid file path: {e}",
                    ),
                )
                return {}

        # Announce parsing start
        start_time = self.timestamp_service.utc_now()
        self.event_publisher.publish(
            OperationStarted(
                operation_type="parsing",
                resource_path=file_path,
                display_name=file_path.name,
                context={"device_type": "fortigate"},
            ),
        )

        try:
            # Detect encoding and read file
            encoding: str | None = self.file_processing_service.detect_encoding(
                file_path,
            )
            with file_path.open(encoding=encoding) as f:
                lines: list[str] = f.readlines()

            # Parse the lines (this is where all the state is managed)
            result = self.parse_lines(lines, file_path)

        except (OSError, UnicodeDecodeError) as e:
            self.event_publisher.publish(
                OperationError(
                    operation_type="parsing",
                    resource_path=file_path,
                    display_name=file_path.name,
                    error_message=str(e),
                ),
            )
            return {}
        else:
            # Announce successful completion
            self.event_publisher.publish(
                OperationCompleted(
                    operation_type="parsing",
                    resource_path=file_path,
                    display_name=file_path.name,
                    success=True,
                    duration=self.timestamp_service.elapsed_seconds(start_time),
                    results={"sections_count": len(result)},
                ),
            )

            return result

    def parse_lines(self, lines: list[str], file_path: Path) -> dict[str, Any]:
        """Parse configuration lines with local state management."""
        # All state is local to this method call - makes parser stateless
        config_data: dict[str, Any] = {
            "_device_metadata": {
                "hardware": None,
                "sw_version": None,
            },
        }
        context_stack: list[dict[str, Any]] = [config_data]
        current_path: list[str] = []

        for line_num, line in enumerate(lines, 1):
            cleaned_line: str = line.rstrip()
            try:
                self._parse_line(cleaned_line, context_stack, current_path)
            except UnrecognizedLineFormatError as e:
                # Publish error to event bus and continue processing
                self.event_publisher.publish(
                    OperationError(
                        operation_type="parsing",
                        resource_path=file_path,
                        display_name=file_path.name,
                        error_message=f"Unrecognized line format: {e.line_content}",
                        error_context={
                            "line_number": line_num,
                            "line_content": cleaned_line,
                            "expected_patterns": e.expected_patterns,
                            "device_type": e.device_type,
                            "config_path": " > ".join(current_path)
                            if current_path
                            else "root",
                        },
                    ),
                )
                continue
            except Exception as e:  # noqa: BLE001
                self.event_publisher.publish(
                    OperationError(
                        operation_type="parsing",
                        resource_path=file_path,
                        display_name=file_path.name,
                        error_message=str(e),
                        error_context={
                            "line_number": line_num,
                            "line_content": cleaned_line,
                            "config_path": " > ".join(current_path)
                            if current_path
                            else "root",
                        },
                    ),
                )
                continue

        return config_data

    def _parse_line(
        self,
        line: str,
        context_stack: list[dict[str, Any]],
        current_path: list[str],
    ) -> None:
        """Parse a single configuration line with provided state."""
        # Check for config-version line first (before general comment pattern)
        if match := self.patterns["config_version"].match(line):
            self._handle_config_version(match.group(1), match.group(2), context_stack)
            return

        # Skip comments and empty lines
        if self.patterns["comment"].match(line) or self.patterns["empty"].match(line):
            return

        # Try each pattern type
        if match := self.patterns["config"].match(line):
            self._handle_config(match.group(1), context_stack, current_path)

        elif match := self.patterns["edit"].match(line):
            self._handle_edit(match.group(1), context_stack, current_path)

        elif match := self.patterns["set"].match(line):
            self._handle_set(match.group(1), match.group(2), context_stack)

        elif match := self.patterns["unset"].match(line):
            self._handle_unset(match.group(1), context_stack)

        elif self.patterns["next"].match(line):
            self._handle_next(context_stack, current_path)

        elif self.patterns["end"].match(line):
            self._handle_end(context_stack, current_path)

        else:
            raise UnrecognizedLineFormatError(
                line_content=line,
                device_type="fortigate",
                expected_patterns=list(self.patterns.keys()),
            )

    def _handle_config_version(
        self,
        device_info: str,
        _additional_info: str,
        context_stack: list[dict[str, Any]],
    ) -> None:
        """
        Handle config-version lines to extract device hardware and software version.

        Example line: #config-version=FGT60F-7.6.3-FW-build3510-250415:opmode=1:vdom=0:user=admin
        Extracts: hardware=FGT60F, sw_version=7.6.3-FW-build3510
        """
        # Split device_info to extract hardware and software version
        # Format is typically: HARDWARE-VERSION-FW-buildXXXX-YYMMDD
        minimum_parts_count = 2
        parts = device_info.split("-", 1)  # Split on first dash only
        if len(parts) >= minimum_parts_count:
            hardware = parts[0]  # e.g., FGT60F
            version_part = parts[1]  # e.g., 7.6.3-FW-build3510-250415

            # Extract version up to the build info
            # Look for pattern like "7.6.3-FW-build3510"
            version_match = re.match(r"^([^-]+(?:-[^-]+)*?)-build\d+", version_part)
            if version_match:
                sw_version = version_match.group(1)  # e.g., 7.6.3-FW
            else:
                # Fallback: take everything before the last dash (if it exists)
                version_parts = version_part.rsplit("-", 1)
                sw_version = (
                    version_parts[0] if len(version_parts) > 1 else version_part
                )

            # Store in device metadata
            root_config = context_stack[0]
            if "_device_metadata" in root_config:
                root_config["_device_metadata"]["hardware"] = hardware
                root_config["_device_metadata"]["sw_version"] = sw_version

                # Publish event to notify about extracted device metadata
                self.event_publisher.publish(
                    OperationCompleted(
                        operation_type="device_metadata_extraction",
                        success=True,
                        duration=0.0,  # Instantaneous operation
                        results={
                            "hardware": hardware,
                            "sw_version": sw_version,
                            "source": "config_version_line",
                        },
                    ),
                )

    def _handle_config(
        self,
        config_path: str,
        context_stack: list[dict[str, Any]],
        current_path: list[str],
    ) -> None:
        """Handle 'config <path>' lines."""
        # Treat the entire config path as a single key
        # e.g., "system global" is ONE config section, not "system" with child "global"
        self.event_publisher.publish(
            OperationStarted(
                operation_type="parsing",
                resource_path=None,  # Will be set by calling method
                context={
                    "config_path": config_path,
                    "action": "config_section_entered",
                },
            ),
        )

        # Create the config section if it doesn't exist
        current_dict = context_stack[-1]
        if config_path not in current_dict:
            current_dict[config_path] = {}

        # Push new context
        context_stack.append(current_dict[config_path])
        current_path.append(config_path)

    def _handle_edit(
        self,
        edit_name: str,
        context_stack: list[dict[str, Any]],
        current_path: list[str],
    ) -> None:
        """Handle 'edit "name"' lines."""
        # Create edit section if it doesn't exist
        current_dict = context_stack[-1]
        if edit_name not in current_dict:
            current_dict[edit_name] = {}

        # Push edit context
        context_stack.append(current_dict[edit_name])
        current_path.append(edit_name)

    def _handle_set(
        self,
        param_name: str,
        param_value: str,
        context_stack: list[dict[str, Any]],
    ) -> None:
        """Handle 'set <param> <value>' lines."""
        # Clean up value (remove quotes, handle special cases)
        value = self.value_cleaner.clean_value(param_value)

        # Set in current context
        current_dict = context_stack[-1]
        current_dict[param_name] = value

    def _handle_unset(
        self,
        param_name: str,
        context_stack: list[dict[str, Any]],
    ) -> None:
        """Handle 'unset <param>' lines."""
        current_dict = context_stack[-1]
        # Store as special marker or remove if exists
        current_dict[param_name] = None

    def _handle_next(
        self,
        context_stack: list[dict[str, Any]],
        current_path: list[str],
    ) -> None:
        """Handle 'next' lines (exit edit block)."""
        if len(context_stack) > 1 and len(current_path) > 0:
            context_stack.pop()
            current_path.pop()

    def _handle_end(
        self,
        context_stack: list[dict[str, Any]],
        current_path: list[str],
    ) -> None:
        """Handle 'end' lines (exit config block)."""
        if len(context_stack) > 1:
            # Pop one level for each 'end'
            # This assumes proper nesting (which FortiGate configs have)
            context_stack.pop()
            if len(current_path) > 0:
                current_path.pop()
