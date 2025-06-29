"""Logging utilities."""

import logging
from pathlib import Path


def setup_logging(
    level: str = "INFO", log_file: Path | None = None, verbose: bool = False
) -> logging.Logger:
    """Set up logging configuration.

    Args:
        level: Logging level
        log_file: Log file path
        verbose: Enable verbose logging

    Returns:
        Configured logger
    """
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Set up handlers
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)

    # Configure logger
    logger = logging.getLogger("network_security_scanner")
    logger.setLevel(getattr(logging, level.upper()))

    for handler in handlers:
        logger.addHandler(handler)

    return logger
