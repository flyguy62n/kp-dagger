#!/usr/bin/env python3
"""
Test script to demonstrate Rich-formatted CLI help pages.

This script shows how the enhanced help formatting looks compared to standard Click output.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import contextlib

from kp_dagger.cli.main import main


def demo_help_pages() -> None:
    """Demonstrate Rich-formatted help pages."""
    print("🎨 Dagger Rich Help Demo")
    print("=" * 50)

    # Test main help
    print("\n1. Main CLI Help:")
    print("-" * 20)
    with contextlib.suppress(SystemExit):
        main(["--help"], standalone_mode=False)

    # Test analyze command help
    print("\n2. Analyze Command Help:")
    print("-" * 30)
    with contextlib.suppress(SystemExit):
        main(["analyze", "--help"], standalone_mode=False)

    # Test validate command help
    print("\n3. Validate Command Help:")
    print("-" * 30)
    with contextlib.suppress(SystemExit):
        main(["validate", "--help"], standalone_mode=False)


if __name__ == "__main__":
    demo_help_pages()
