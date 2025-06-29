"""Scan command for analyzing configuration files."""

from pathlib import Path

import click
from pybastion.cli.options import database_options, output_options
from pybastion.core.scanner import NetworkScanner
from pybastion.models.base.enums import DeviceType
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@click.group(name="scan")
def scan_group() -> None:
    """Scan network device configurations for security issues."""


@scan_group.command()
@click.argument("config_files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--device-type",
    type=click.Choice([t.value for t in DeviceType], case_sensitive=False),
    help="Device type (auto-detect if not specified)",
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Recursively scan directories for config files",
)
@database_options
@output_options
@click.pass_context
def files(
    ctx: click.Context,
    config_files: tuple[Path, ...],
    device_type: str | None,
    recursive: bool,
    database: Path | None,
    memory: bool,
    output: Path | None,
    output_format: str,
) -> None:
    """
    Scan configuration files for security issues.

    Analyzes one or more network device configuration files for:
    - Security vulnerabilities
    - Compliance violations
    - Best practice deviations
    - Access control issues
    """
    if not config_files:
        console.print("[red]Error: No configuration files specified[/red]")
        ctx.exit(1)

    verbose = ctx.obj.get("verbose", False)

    try:
        scanner = NetworkScanner(
            database_path=":memory:" if memory else database,
            verbose=verbose,
        )

        # Collect all files to scan
        files_to_scan = []
        for config_file in config_files:
            if config_file.is_dir() and recursive:
                # Find all config files in directory
                patterns = ["*.cfg", "*.conf", "*.txt", "*.config"]
                for pattern in patterns:
                    files_to_scan.extend(config_file.rglob(pattern))
            elif config_file.is_file():
                files_to_scan.append(config_file)

        if not files_to_scan:
            console.print("[yellow]No configuration files found[/yellow]")
            return

        console.print(
            f"[blue]Scanning {len(files_to_scan)} configuration files...[/blue]",
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Scanning files...", total=len(files_to_scan))

            results = []
            for config_file in files_to_scan:
                progress.update(task, description=f"Scanning {config_file.name}")

                try:
                    result = scanner.scan_file(
                        config_file,
                        device_type=DeviceType(device_type) if device_type else None,
                    )
                    results.append(result)
                except Exception as e:
                    console.print(f"[red]Error scanning {config_file}: {e}[/red]")
                    if verbose:
                        console.print_exception()

                progress.advance(task)

        # Generate and save report
        if results:
            report = scanner.generate_report(results, output_format)

            if output:
                output.write_text(report)
                console.print(f"[green]Report saved to {output}[/green]")
            else:
                console.print(report)
        else:
            console.print("[yellow]No results to report[/yellow]")

    except Exception as e:
        console.print(f"[red]Scan failed: {e}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
