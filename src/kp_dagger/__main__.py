"""
PyBastion package entry point for python -m pybastion usage.

This module enables running PyBastion as a module:
    python -m pybastion [commands...]
"""

from kp_dagger.cli.main import main

if __name__ == "__main__":
    # NOTE: Container initialization will be added when DI integration is complete
    # For now, run CLI directly until all services are implemented
    main()
