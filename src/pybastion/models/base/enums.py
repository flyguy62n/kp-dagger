"""Common enumerations across all models."""

from enum import Enum


class DeviceType(str, Enum):
    """Supported device types."""

    CISCO_IOS = "cisco-ios"
    CISCO_ASA = "cisco-asa"
    FORTIGATE = "fortigate"
    PALOALTO = "paloalto"


class RuleAction(str, Enum):
    """Access control rule actions."""

    PERMIT = "permit"
    DENY = "deny"
    ALLOW = "allow"
    DROP = "drop"
    REJECT = "reject"


class Protocol(str, Enum):
    """Network protocols."""

    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ESP = "esp"
    AH = "ah"
    GRE = "gre"
    OSPF = "ospf"
    EIGRP = "eigrp"
    IP = "ip"
    ANY = "any"


class Severity(str, Enum):
    """Finding severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(str, Enum):
    """Compliance check status."""

    PASS = "pass"  # noqa: S105
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"
    MANUAL_REVIEW = "manual_review"


class RoutingProtocolType(str, Enum):
    """Routing protocol types."""

    STATIC = "static"
    OSPF = "ospf"
    EIGRP = "eigrp"
    BGP = "bgp"
    RIP = "rip"
    IS_IS = "is-is"


class IPVersion(str, Enum):
    """IP version enumeration."""

    IPV4 = "ipv4"
    IPV6 = "ipv6"


class AddressType(str, Enum):
    """Type of IP address representation."""

    INDIVIDUAL = "individual"  # Single host address (e.g., "192.168.1.1")
    NETWORK = "network"  # Network with CIDR/netmask (e.g., "192.168.1.0/24")
    RANGE = "range"  # Address range (e.g., "192.168.1.10-192.168.1.20")
    WILDCARD = "wildcard"  # Cisco wildcard mask format (e.g., "192.168.1.0 0.0.0.255")
    ANY = "any"  # Special "any" address keyword
