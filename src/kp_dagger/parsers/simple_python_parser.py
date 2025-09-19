"""
Comparison: Python-based hierarchical configuration parser.

This demonstrates a simpler approach using Python data structures
and regex patterns instead of ANTLR4 grammar files.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class FortigateConfigParser:
    """
    Simple Python-based configuration parser using stacks and regex.

    This approach trades grammar formalism for implementation simplicity.
    """

    def __init__(self):
        self.config_data: dict[str, Any] = {}
        self.context_stack: list[dict[str, Any]] = []
        self.current_path: list[str] = []

        # Regex patterns for different line types
        self.patterns = {
            "config": re.compile(r"^\s*config\s+(.+)$"),
            "edit": re.compile(r'^\s*edit\s+"?([^"]+)"?\s*$'),
            "set": re.compile(r"^\s*set\s+(\S+)\s+(.+)$"),
            "unset": re.compile(r"^\s*unset\s+(\S+)$"),
            "next": re.compile(r"^\s*next\s*$"),
            "end": re.compile(r"^\s*end\s*$"),
            "comment": re.compile(r"^\s*#.*$"),
            "empty": re.compile(r"^\s*$"),
        }

    def parse_file(self, file_path: str) -> dict[str, Any]:
        """Parse a FortiGate configuration file."""
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        return self.parse_lines(lines)

    def parse_lines(self, lines: list[str]) -> dict[str, Any]:
        """Parse configuration lines."""
        self.config_data = {}
        self.context_stack = [self.config_data]
        self.current_path = []

        for line_num, line in enumerate(lines, 1):
            try:
                self._parse_line(line.rstrip("\n\r"))
            except Exception as e:
                logger.error(f"Error parsing line {line_num}: {line.strip()}: {e}")
                continue

        return self.config_data

    def _parse_line(self, line: str) -> None:
        """Parse a single configuration line."""
        # Skip comments and empty lines
        if self.patterns["comment"].match(line) or self.patterns["empty"].match(line):
            return

        # Try each pattern type
        if match := self.patterns["config"].match(line):
            self._handle_config(match.group(1))

        elif match := self.patterns["edit"].match(line):
            self._handle_edit(match.group(1))

        elif match := self.patterns["set"].match(line):
            self._handle_set(match.group(1), match.group(2))

        elif match := self.patterns["unset"].match(line):
            self._handle_unset(match.group(1))

        elif self.patterns["next"].match(line):
            self._handle_next()

        elif self.patterns["end"].match(line):
            self._handle_end()

        else:
            logger.debug(f"Unrecognized line format: {line}")

    def _handle_config(self, config_path: str) -> None:
        """Handle 'config <path>' lines."""
        # Treat the entire config path as a single key
        # e.g., "system global" is ONE config section, not "system" with child "global"
        logger.debug(f"Entering config: {config_path}")

        # Create the config section if it doesn't exist
        current_dict = self.context_stack[-1]
        if config_path not in current_dict:
            current_dict[config_path] = {}

        # Push new context
        self.context_stack.append(current_dict[config_path])
        self.current_path.append(config_path)

    def _handle_edit(self, edit_name: str) -> None:
        """Handle 'edit "name"' lines."""
        logger.debug(f"Entering edit: {edit_name}")

        # Create edit section if it doesn't exist
        current_dict = self.context_stack[-1]
        if edit_name not in current_dict:
            current_dict[edit_name] = {}

        # Push edit context
        self.context_stack.append(current_dict[edit_name])
        self.current_path.append(edit_name)

    def _handle_set(self, param_name: str, param_value: str) -> None:
        """Handle 'set <param> <value>' lines."""
        # Clean up value (remove quotes, handle special cases)
        value = self._clean_value(param_value)

        logger.debug(f"Setting {param_name} = {value}")

        # Set in current context
        current_dict = self.context_stack[-1]
        current_dict[param_name] = value

    def _handle_unset(self, param_name: str) -> None:
        """Handle 'unset <param>' lines."""
        logger.debug(f"Unsetting {param_name}")

        current_dict = self.context_stack[-1]
        # Store as special marker or remove if exists
        current_dict[param_name] = None

    def _handle_next(self) -> None:
        """Handle 'next' lines (exit edit block)."""
        if len(self.context_stack) > 1 and len(self.current_path) > 0:
            logger.debug(f"Exiting edit: {self.current_path[-1]}")
            self.context_stack.pop()
            self.current_path.pop()

    def _handle_end(self) -> None:
        """Handle 'end' lines (exit config block)."""
        if len(self.context_stack) > 1:
            # Pop one level for each 'end'
            # This assumes proper nesting (which FortiGate configs have)
            self.context_stack.pop()
            if len(self.current_path) > 0:
                removed = self.current_path.pop()
                logger.debug("Exiting config level: %s", removed)

    def _clean_value(self, value: str) -> Any:
        """Clean and convert parameter values."""
        value = value.strip()

        # Remove surrounding quotes
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]

        # Handle special values
        if value.lower() in ["enable", "disable"]:
            return value.lower() == "enable"

        # Try to convert to number
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Handle IP addresses, maintain as string
        if re.match(r"^\d+\.\d+\.\d+\.\d+", value):
            return value

        # Handle IPv6 addresses
        if ":" in value and ("::" in value or len(value.split(":")) > 4):
            return value

        return value


def analyze_interface_security_simple(config_data: dict[str, Any]) -> dict[str, Any]:
    """
    Simple interface security analysis using parsed config data.

    This shows how analysis becomes simpler with direct data structures.
    """
    # With corrected structure: "system interface" is a single config section
    interfaces = config_data.get("system interface", {})

    analysis = {
        "total_interfaces": len(interfaces),
        "interfaces_up": 0,
        "interfaces_down": 0,
        "ipv6_enabled": 0,
        "dual_stack": 0,
        "security_issues": [],
        "interface_details": {},
    }

    for iface_name, iface_config in interfaces.items():
        status = iface_config.get("status", "unknown")
        has_ipv4 = bool(iface_config.get("ip"))
        has_ipv6 = bool(iface_config.get("ipv6", {}).get("ip6-address"))

        # Count interface states
        if status == "up":
            analysis["interfaces_up"] += 1
        elif status == "down":
            analysis["interfaces_down"] += 1

        # Count IPv6 and dual-stack
        if has_ipv6:
            analysis["ipv6_enabled"] += 1
        if has_ipv4 and has_ipv6:
            analysis["dual_stack"] += 1

        # Security analysis
        allowaccess = iface_config.get("allowaccess", "") or ""
        if "ssh" in allowaccess or "https" in allowaccess:
            analysis["security_issues"].append(
                f"Interface {iface_name} allows management access: {allowaccess}",
            )

        analysis["interface_details"][iface_name] = {
            "status": status,
            "has_ipv4": has_ipv4,
            "has_ipv6": has_ipv6,
            "allowaccess": allowaccess,
            "type": iface_config.get("type", "unknown"),
        }

    return analysis


if __name__ == "__main__":
    # Enable limited debug logging
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

    # Test the simple parser
    parser = ConfigParser()

    # Test with your interface config file
    config_data = parser.parse_file(
        r"D:\Users\Randy\Downloads\Git\kp-dagger\src\kp_dagger\parsers\test_interface_ipv6.txt",
    )

    # Print structure (limited for readability)
    print("=== PARSED CONFIG STRUCTURE ===")
    print("Top-level config sections:")
    for section in config_data.keys():
        print(f"  - {section}")

    import json

    interfaces = config_data.get("system interface", {})
    print(f"Found {len(interfaces)} interfaces:")
    for name in list(interfaces.keys())[:5]:  # Show first 5
        print(f"  - {name}")
    if len(interfaces) > 5:
        print(f"  ... and {len(interfaces) - 5} more")

    # Show first interface detail
    if interfaces:
        first_iface = next(iter(interfaces))
        print(f"\nFirst interface ({first_iface}) details:")
        print(json.dumps(interfaces[first_iface], indent=2, default=str)[:500] + "...")

    # Analyze interfaces
    print("\n=== INTERFACE SECURITY ANALYSIS ===")
    analysis = analyze_interface_security_simple(config_data)
    print(json.dumps(analysis, indent=2, default=str))
