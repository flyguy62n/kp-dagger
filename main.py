"""
Development convenience entry point for Dagger.

⚠️  This file is for development convenience only.

For production usage, use one of these methods:
    1. uv run kp_dagger [commands...]
    2. python -m kp_dagger [commands...]
    3. pip install -e . && kp_dagger [commands...]

This file may be removed in future versions.
"""

from kp_dagger.cli.main import main


def run_application() -> None:
    """Initialize and run the KP-Dagger application."""
    print(
        "⚠️  Using development entry point. Consider using 'uv run kp_dagger' instead.",
    )

    # NOTE: Container initialization will be added when DI integration is complete
    # For now, run CLI directly until all services are implemented
    main()


if __name__ == "__main__":
    run_application()
