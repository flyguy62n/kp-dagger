"""Core PyBastion scanner implementation."""

from pathlib import Path
from typing import Any

from dependency_injector.wiring import Provide, inject

from pybastion.containers import ApplicationContainer
from pybastion.core.database import DatabaseManager
from pybastion.core.exceptions import (
    NetworkScannerError,
    UnsupportedDeviceError,
)
from pybastion.models.base.enums import DeviceType, ReportFormat
from pybastion.parsers.factory import ParserFactory


class PyBastionScanner:
    """Main scanner class for analyzing network device configurations."""

    @inject
    def __init__(
        self,
        database_manager: DatabaseManager = Provide[
            ApplicationContainer.core_container.database_manager
        ],
        parser_factory: ParserFactory = Provide[
            ApplicationContainer.parser_container.parser_factory
        ],
        analyzers: Any = Provide[ApplicationContainer.analyzer_container],
        reporters: Any = Provide[ApplicationContainer.report_container],
        verbose: bool = False,
    ) -> None:
        """
        Initialize the network scanner.

        Args:
            database_manager: Database manager instance
            parser_factory: Parser factory instance
            analyzers: Analyzer services container
            reporters: Reporter services container
            verbose: Enable verbose logging

        """
        self.verbose = verbose
        self.database = database_manager
        self.parser_factory = parser_factory
        self.analyzers = analyzers
        self.reporters = reporters

        # Initialize database
        self.database.initialize()

    def scan_file(
        self,
        config_file: Path,
        device_type: DeviceType | None = None,
    ) -> dict[str, Any]:
        """
        Scan a single configuration file.

        Args:
            config_file: Path to configuration file
            device_type: Device type (auto-detected if None)

        Returns:
            Dictionary containing scan results

        Raises:
            NetworkScannerError: If scanning fails

        """
        if not config_file.exists():
            msg = f"Configuration file not found: {config_file}"
            raise NetworkScannerError(msg)

        try:
            # Read configuration file
            config_text = config_file.read_text(encoding="utf-8")

            # Auto-detect device type if not provided
            if device_type is None:
                device_type = self._detect_device_type(config_text)

            # Get parser for device type
            parser = self.parser_factory.get_parser(device_type)

            # Parse configuration
            parsed_config = parser.parse(config_text)

            # Store in database
            device_id = self.database.store_device_config(
                device_type=device_type,
                config_file=config_file,
                parsed_config=parsed_config,
            )

            # Run security analysis
            findings = self._analyze_configuration(device_id, parsed_config)

            return {
                "device_id": device_id,
                "device_type": device_type.value,
                "config_file": str(config_file),
                "findings": findings,
                "total_findings": len(findings),
                "severity_counts": self._count_severities(findings),
            }

        except Exception as e:
            msg = f"Failed to scan {config_file}: {e}"
            raise NetworkScannerError(msg) from e

    def _detect_device_type(self, config_text: str) -> DeviceType:
        """
        Auto-detect device type from configuration text.

        Args:
            config_text: Configuration file content

        Returns:
            Detected device type

        Raises:
            UnsupportedDeviceError: If device type cannot be detected

        """
        # Simple heuristic-based detection
        config_lower = config_text.lower()

        # Check for Cisco IOS patterns
        if any(
            pattern in config_lower
            for pattern in [
                "version ",
                "hostname ",
                "interface ",
                "router ",
                "access-list ",
                "ip route",
                "line vty",
            ]
        ):
            return DeviceType.CISCO_IOS

        # Check for Cisco ASA patterns
        if any(
            pattern in config_lower
            for pattern in ["asa version", "access-group", "object-group", "nat "]
        ):
            return DeviceType.CISCO_ASA

        # Check for FortiGate patterns
        if any(
            pattern in config_lower
            for pattern in ["config system", "config firewall", "edit ", "next", "end"]
        ):
            return DeviceType.FORTIGATE

        # Check for PAN-OS patterns
        if any(
            pattern in config_lower
            for pattern in ["<config", "<entry name", "<member>", "</config>"]
        ):
            return DeviceType.PALOALTO

        supported_types = [t.value for t in DeviceType]
        raise UnsupportedDeviceError("unknown", supported_types)

    def _analyze_configuration(
        self,
        device_id: str,
        parsed_config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Analyze parsed configuration for security issues.

        Args:
            device_id: Device identifier
            parsed_config: Parsed configuration data

        Returns:
            List of security findings

        """
        # TODO: Implement security analysis
        # This would involve:
        # 1. Running CIS benchmark checks
        # 2. Analyzing access control lists
        # 3. Checking for security best practices
        # 4. Validating configuration settings

        findings = []

        # Placeholder finding for demonstration
        findings.append(
            {
                "id": "demo-finding-001",
                "title": "Configuration analysis placeholder",
                "description": "This is a placeholder finding for demonstration",
                "severity": "low",
                "category": "configuration",
                "device_id": device_id,
            },
        )

        return findings

    def _count_severities(self, findings: list[dict[str, Any]]) -> dict[str, int]:
        """
        Count findings by severity level.

        Args:
            findings: List of security findings

        Returns:
            Dictionary with severity counts

        """
        counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        for finding in findings:
            severity = finding.get("severity", "low")
            if severity in counts:
                counts[severity] += 1

        return counts

    def generate_report(
        self,
        results: list[dict[str, Any]],
        format_type: str = "json",
    ) -> str:
        """
        Generate a report from scan results.

        Args:
            results: List of scan results
            format_type: Report format (json, html, excel)

        Returns:
            Generated report as string

        Raises:
            NetworkScannerError: If report generation fails

        """
        try:
            if format_type.lower() == "json":
                import json

                return json.dumps(results, indent=2)

            if format_type.lower() == "html":
                return self._generate_html_report(results)

            if format_type.lower() == "excel":
                # For Excel, we'd return the file path instead of content
                return "Excel report generation not yet implemented"

            supported_formats = [f.value for f in ReportFormat]
            msg = f"Unsupported report format: {format_type}. Supported: {supported_formats}"
            raise NetworkScannerError(msg)

        except Exception as e:
            msg = f"Failed to generate {format_type} report: {e}"
            raise NetworkScannerError(msg) from e

    def _generate_html_report(self, results: list[dict[str, Any]]) -> str:
        """
        Generate HTML report from results.

        Args:
            results: List of scan results

        Returns:
            HTML report as string

        """
        # Simple HTML template for demonstration
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Network Security Scan Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { background-color: #f0f0f0; padding: 20px; }
                .result { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
                .severity-critical { border-left: 5px solid #d32f2f; }
                .severity-high { border-left: 5px solid #f57c00; }
                .severity-medium { border-left: 5px solid #fbc02d; }
                .severity-low { border-left: 5px solid #388e3c; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Network Security Scan Report</h1>
                <p>Generated scan results for network device configurations</p>
            </div>
        """

        for result in results:
            html += f"""
            <div class="result">
                <h2>Device: {result.get("device_type", "Unknown")}</h2>
                <p><strong>File:</strong> {result.get("config_file", "Unknown")}</p>
                <p><strong>Total Findings:</strong> {result.get("total_findings", 0)}</p>
                <p><strong>Severity Breakdown:</strong> {result.get("severity_counts", {})}</p>
            </div>
            """

        html += """
        </body>
        </html>
        """

        return html


# Keep backward compatibility
Scanner = PyBastionScanner
NetworkScanner = PyBastionScanner  # Backward compatibility alias
