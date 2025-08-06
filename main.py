"""
Development convenience entry point for PyBastion.

⚠️  This file is for development convenience only.

For production usage, use one of these methods:
    1. uv run pybastion [commands...]
    2. python -m pybastion [commands...]
    3. pip install -e . && pybastion [commands...]

This file may be removed in future versions.
"""

from kp_dagger.cli.main import main


def run_application() -> None:
    """Initialize and run the PyBastion application."""
    print(
        "⚠️  Using development entry point. Consider using 'uv run pybastion' instead.",
    )

    # NOTE: Container initialization will be added when DI integration is complete
    # For now, run CLI directly until all services are implemented
    main()


if __name__ == "__main__":
    run_application()
