"""Utility functions for network operations."""

import ipaddress


def validate_ip_address(ip_str: str) -> bool:
    """Validate IP address format.

    Args:
        ip_str: IP address string

    Returns:
        True if valid IP address, False otherwise
    """
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def validate_network(network_str: str) -> bool:
    """Validate network address in CIDR notation.

    Args:
        network_str: Network address string

    Returns:
        True if valid network address, False otherwise
    """
    try:
        ipaddress.ip_network(network_str, strict=False)
        return True
    except ValueError:
        return False


def normalize_mac_address(mac_str: str) -> str:
    """Normalize MAC address format.

    Args:
        mac_str: MAC address string

    Returns:
        Normalized MAC address
    """
    # TODO: Implement MAC address normalization
    return mac_str.lower().replace("-", ":").replace(".", ":")


def parse_port_range(port_str: str) -> tuple[int, int]:
    """Parse port range string.

    Args:
        port_str: Port range string (e.g., "80", "80-443")

    Returns:
        Tuple of start and end ports
    """
    if "-" in port_str:
        start, end = port_str.split("-")
        return int(start), int(end)
    else:
        port = int(port_str)
        return port, port
