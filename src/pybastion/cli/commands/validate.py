"""
Validate command for PyBastion CLI.

Handles configuration file validation including syntax checking and basic structure validation.
"""

from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from pybastion.cli.utils.output import RichCommand, error_console, success_console

console = Console()


@click.command(cls=RichCommand)
@click.argument(
    "config_files",
    nargs=-1,
    type=click.Path(exists=True, path_type=Path),
    required=True,
)
@click.option(
    "--device-type",
    type=click.Choice(
        ["auto", "cisco-ios", "cisco-asa", "fortigate", "paloalto"],
        case_sensitive=False,
    ),
    default="auto",
    help="Device type for configuration validation (default: auto-detect).",
)
@click.option(
    "--strict",
    is_flag=True,
    help="Enable strict validation mode (treat warnings as errors).",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file for validation results (default: stdout).",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"], case_sensitive=False),
    default="table",
    help="Output format for validation results.",
)
@click.pass_context
def validate(
    ctx: click.Context,
    config_files: tuple[Path, ...],
    device_type: str,
    strict: bool,
    output: Path | None,
    output_format: str,
) -> None:
    """
    Validate network device configuration files for syntax and structure.

    ⚠️  WARNING: This is a development version and is not ready for production use.

    CONFIG_FILES: One or more configuration files to validate.

    Examples:
        # Validate a single configuration file
        pybastion validate router-config.txt

        # Validate multiple files with specific device type
        pybastion validate --device-type cisco-ios *.cfg

        # Strict validation mode
        pybastion validate --strict config.txt

        # Save validation results to JSON
        pybastion validate --format json --output validation.json config.txt

    """
    verbose = ctx.obj.get("verbose", 0)
    quiet = ctx.obj.get("quiet", False)

    if not quiet:
        console.print("\n✅ [bold blue]Starting Configuration Validation[/bold blue]\n")

    # Display validation configuration
    if verbose > 0:
        _show_validation_config(config_files, device_type, strict, output_format)

    validation_results = []

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            validate_task = progress.add_task(
                "Validating configuration files...",
                total=len(config_files),
            )

            for config_file in config_files:
                if verbose > 1:
                    console.print(f"  📄 Validating: {config_file}")

                # Perform validation for each file
                result = _validate_config_file(config_file, device_type, strict)
                validation_results.append(result)

                progress.advance(validate_task)

        # Display results
        if not quiet:
            _show_validation_results(validation_results, output_format)

        # Save output if specified
        if output:
            _save_validation_results(output, validation_results, output_format)
            success_console.print(f"✅ Validation results saved to: {output}")

        # Exit with error code if validation failed
        failed_count = sum(1 for result in validation_results if not result["valid"])
        if failed_count > 0:
            if not quiet:
                error_console.print(f"❌ Validation failed for {failed_count} file(s)")
            ctx.exit(1)

    except Exception as e:
        error_console.print(f"❌ Validation failed: {e}")
        if verbose > 0:
            console.print_exception()
        ctx.exit(1)


def _show_validation_config(
    config_files: tuple[Path, ...],
    device_type: str,
    strict: bool,
    output_format: str,
) -> None:
    """Display validation configuration details."""
    table = Table(title="Validation Configuration", show_header=False)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Files", f"{len(config_files)} configuration file(s)")
    table.add_row("Device Type", device_type)
    table.add_row("Strict Mode", "Yes" if strict else "No")
    table.add_row("Output Format", output_format)

    console.print(table)
    console.print()


def _validate_config_file(config_file: Path, device_type: str, strict: bool) -> dict:
    """Validate a single configuration file."""
    # Implementation will perform actual validation
    # This is a placeholder that returns mock results

    result = {
        "file": str(config_file),
        "device_type": device_type
        if device_type != "auto"
        else "cisco-ios",  # Mock detection
        "valid": True,
        "errors": [],
        "warnings": [],
        "info": {
            "lines": 150,  # Mock line count
            "size": config_file.stat().st_size,
        },
    }

    # Mock some validation issues for demonstration
    if "bad" in config_file.name.lower():
        result["valid"] = False
        result["errors"].append("Invalid command syntax on line 42")

    if "warn" in config_file.name.lower():
        result["warnings"].append("Deprecated command on line 15")
        if strict:
            result["valid"] = False

    return result


def _show_validation_results(
    validation_results: list[dict],
    output_format: str,
) -> None:
    """Display validation results."""
    console.print("📋 [bold green]Validation Results[/bold green]\n")

    if output_format == "table":
        results_table = Table(title="File Validation Summary")
        results_table.add_column("File", style="cyan")
        results_table.add_column("Device Type", style="white")
        results_table.add_column("Status", style="white")
        results_table.add_column("Errors", style="white")
        results_table.add_column("Warnings", style="white")

        for result in validation_results:
            file_name = Path(result["file"]).name
            device_type = result["device_type"]
            status = "✅ VALID" if result["valid"] else "❌ INVALID"
            error_count = len(result["errors"])
            warning_count = len(result["warnings"])

            results_table.add_row(
                file_name,
                device_type,
                status,
                str(error_count) if error_count > 0 else "-",
                str(warning_count) if warning_count > 0 else "-",
            )

        console.print(results_table)

        # Show detailed errors/warnings if any
        for result in validation_results:
            if result["errors"] or result["warnings"]:
                console.print(f"\n📄 [bold]{Path(result['file']).name}[/bold]:")
                for error in result["errors"]:
                    console.print(f"  ❌ ERROR: {error}")
                for warning in result["warnings"]:
                    console.print(f"  ⚠️  WARNING: {warning}")

    else:
        # For JSON/YAML output, we'll just show a summary in the console
        valid_count = sum(1 for result in validation_results if result["valid"])
        total_count = len(validation_results)
        console.print(f"Validation complete: {valid_count}/{total_count} files passed")


def _save_validation_results(
    output: Path,
    validation_results: list[dict],
    output_format: str,
) -> None:
    """Save validation results to file."""
    output.parent.mkdir(parents=True, exist_ok=True)

    if output_format == "json":
        import json

        with output.open("w", encoding="utf-8") as f:
            json.dump(validation_results, f, indent=2)
    elif output_format == "yaml":
        try:
            import yaml

            with output.open("w", encoding="utf-8") as f:
                yaml.dump(validation_results, f, default_flow_style=False)
        except ImportError:
            # Fallback to JSON if YAML not available
            import json

            with output.open("w", encoding="utf-8") as f:
                json.dump(validation_results, f, indent=2)
    elif output_format == "table":
        # Save as formatted text table
        with output.open("w", encoding="utf-8") as f:
            f.write("Configuration Validation Results\n")
            f.write("=" * 40 + "\n\n")
            for result in validation_results:
                f.write(f"File: {result['file']}\n")
                f.write(f"Device Type: {result['device_type']}\n")
                f.write(f"Valid: {'Yes' if result['valid'] else 'No'}\n")
                if result["errors"]:
                    f.write("Errors:\n")
                    for error in result["errors"]:
                        f.write(f"  - {error}\n")
                if result["warnings"]:
                    f.write("Warnings:\n")
                    for warning in result["warnings"]:
                        f.write(f"  - {warning}\n")
                f.write("\n")
