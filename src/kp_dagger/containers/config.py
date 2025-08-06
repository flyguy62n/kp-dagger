"""Configuration management for dependency injection."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration."""

    path: str = Field(default=":memory:", description="Database file path")


class EncryptionConfig(BaseModel):
    """Encryption configuration."""

    master_key: str = Field(description="Master encryption key")
    salt: str = Field(description="Encryption salt")


class CoreConfig(BaseModel):
    """Core services configuration."""

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    encryption: EncryptionConfig


class CveApiConfig(BaseModel):
    """CVE API client configuration."""

    api_key: str = Field(description="CVE Details API key")
    base_url: str = Field(
        default="https://www.cvedetails.com/api/",
        description="CVE API base URL",
    )
    timeout: int = Field(default=30, description="Request timeout in seconds")
    rate_limit: int = Field(default=100, description="Requests per minute")


class EolApiConfig(BaseModel):
    """End of Life API client configuration."""

    base_url: str = Field(
        default="https://endoflife.date/api/",
        description="EOL API base URL",
    )
    timeout: int = Field(default=30, description="Request timeout in seconds")
    rate_limit: int = Field(default=1000, description="Requests per minute")


class ApiClientConfig(BaseModel):
    """API clients configuration."""

    cve: CveApiConfig
    eol: EolApiConfig = Field(default_factory=EolApiConfig)


class ParserConfig(BaseModel):
    """Parser configuration."""

    max_file_size: int = Field(
        default=100 * 1024 * 1024,
        description="Maximum config file size in bytes",
    )
    encoding: str = Field(default="utf-8", description="Default file encoding")


class ComplianceConfig(BaseModel):
    """Compliance analyzer configuration."""

    cis_level: int = Field(default=1, description="CIS benchmark level to check")
    include_level2: bool = Field(default=False, description="Include Level 2 checks")


class RiskConfig(BaseModel):
    """Risk analyzer configuration."""

    severity_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "critical": 10.0,
            "high": 7.5,
            "medium": 5.0,
            "low": 2.5,
            "info": 1.0,
        },
        description="Severity score weights",
    )


class AnalyzerConfig(BaseModel):
    """Analyzer configuration."""

    compliance: ComplianceConfig = Field(default_factory=ComplianceConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)


class TemplateConfig(BaseModel):
    """Report template configuration."""

    html_path: str = Field(
        default="templates/html",
        description="HTML template directory",
    )
    excel_path: str = Field(
        default="templates/excel",
        description="Excel template directory",
    )


class ReportConfig(BaseModel):
    """Report generation configuration."""

    templates: TemplateConfig = Field(default_factory=TemplateConfig)
    output_dir: str = Field(default="reports", description="Default output directory")


class ScannerConfig(BaseModel):
    """Scanner configuration."""

    verbose: bool = Field(default=False, description="Enable verbose logging")
    parallel_workers: int = Field(default=4, description="Number of parallel workers")


class PyBastionConfig(BaseModel):
    """Main PyBastion configuration."""

    core: CoreConfig
    api_clients: ApiClientConfig
    parsers: ParserConfig = Field(default_factory=ParserConfig)
    analyzers: AnalyzerConfig = Field(default_factory=AnalyzerConfig)
    reports: ReportConfig = Field(default_factory=ReportConfig)
    scanner: ScannerConfig = Field(default_factory=ScannerConfig)


def load_config(config_path: str | Path) -> dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary

    """
    config_file = Path(config_path)

    if not config_file.exists():
        msg = f"Configuration file not found: {config_path}"
        raise FileNotFoundError(msg)

    with config_file.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_config(config_dict: dict[str, Any]) -> PyBastionConfig:
    """
    Validate configuration dictionary.

    Args:
        config_dict: Configuration dictionary

    Returns:
        Validated configuration object

    """
    return PyBastionConfig.model_validate(config_dict)
