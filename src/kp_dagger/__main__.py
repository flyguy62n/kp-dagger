"""
Dagger package entry point for python -m Dagger usage.

This module enables running Dagger as a module:
    python -m Dagger [commands...]
"""

from kp_dagger.cli.main import main

if __name__ == "__main__":
    # NOTE: Container initialization will be added when DI integration is complete
    # For now, run CLI directly until all services are implemented
    main()
