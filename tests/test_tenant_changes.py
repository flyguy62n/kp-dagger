#!/usr/bin/env python3
"""Test script to validate tenant model changes."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_tenant_model():
    """Test the updated tenant-based models."""
    try:
        from kp_dagger.models.base.enums import AddressType, DeviceType, IPVersion
        from kp_dagger.models.base.tenant import Tenant
        from kp_dagger.models.normalized.device import Device
        from kp_dagger.models.normalized.ip_address import IPAddress

        print("✅ All imports successful")

        # Test tenant creation
        tenant = Tenant(name="Test Tenant", slug="test-tenant")
        print(f"✅ Tenant created: {tenant.name} (ID: {tenant.id})")

        # Test IP address with tenant_id
        ip_addr = IPAddress(
            tenant_id=tenant.id,
            ip_address="192.168.1.1",
            ip_version=IPVersion.IPV4,
            address_type=AddressType.INDIVIDUAL,
            original_format="192.168.1.1",
        )
        print(f"✅ IP Address created: {ip_addr} (Tenant: {ip_addr.tenant_id})")

        # Test device with tenant_id
        device = Device(
            tenant_id=tenant.id,
            hostname="test-router",
            device_type=DeviceType.CISCO_IOS,
        )
        print(f"✅ Device created: {device.hostname} (Tenant: {device.tenant_id})")

        print("🎉 All tenant model changes validated successfully!")
        return True

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


if __name__ == "__main__":
    success = test_tenant_model()
    sys.exit(0 if success else 1)
