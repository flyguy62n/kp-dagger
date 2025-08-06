"""
Unit tests for the encryption system.
"""

from uuid import uuid4

import pytest

from kp_dagger.core.encryption import (
    DecryptionError,
    EncryptionConfigError,
    EncryptionServiceManager,
    KDFConfig,
    TenantEncryptionService,
)


class TestKDFConfig:
    """Test KDF configuration."""

    def test_default_config(self):
        """Test default KDF configuration."""
        config = KDFConfig()
        assert config.algorithm == "argon2id"
        assert config.time_cost == 3
        assert config.memory_cost == 65536
        assert config.parallelism == 1
        assert config.salt_length == 32
        assert config.key_length == 32

    def test_custom_config(self):
        """Test custom KDF configuration."""
        config = KDFConfig(
            algorithm="pbkdf2",
            time_cost=5,
            memory_cost=131072,
            parallelism=2,
            salt_length=16,
            key_length=16,
        )
        assert config.algorithm == "pbkdf2"
        assert config.time_cost == 5
        assert config.memory_cost == 131072
        assert config.parallelism == 2
        assert config.salt_length == 16
        assert config.key_length == 16


class TestTenantEncryptionService:
    """Test tenant encryption service."""

    @pytest.fixture
    def tenant_id(self):
        """Generate test tenant ID."""
        return uuid4()

    @pytest.fixture
    def runtime_key(self):
        """Generate test runtime key."""
        return b"a" * 32

    @pytest.fixture
    def service(self, tenant_id, runtime_key):
        """Create test encryption service."""
        return TenantEncryptionService(tenant_id, runtime_key)

    def test_init_valid(self, tenant_id, runtime_key):
        """Test valid service initialization."""
        service = TenantEncryptionService(tenant_id, runtime_key)
        assert service.tenant_id == tenant_id
        assert service.runtime_key == runtime_key
        assert service.kdf_config.algorithm == "argon2id"

    def test_init_short_key(self, tenant_id):
        """Test initialization with short runtime key."""
        with pytest.raises(EncryptionConfigError, match="at least 32 bytes"):
            TenantEncryptionService(tenant_id, b"short")

    def test_encrypt_decrypt_basic(self, service):
        """Test basic encryption and decryption."""
        plaintext = "Hello, World!"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert isinstance(encrypted, bytes)
        assert len(encrypted) > 0
        assert decrypted == plaintext

    def test_encrypt_decrypt_empty(self, service):
        """Test encryption of empty string."""
        encrypted = service.encrypt("")
        decrypted = service.decrypt(encrypted)

        assert encrypted == b""
        assert decrypted == ""

    def test_encrypt_decrypt_unicode(self, service):
        """Test encryption of unicode strings."""
        plaintext = "Hello, 世界! 🌍"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_deterministic_salt(self, service):
        """Test that encryption produces different results due to random salt."""
        plaintext = "consistent message"
        encrypted1 = service.encrypt(plaintext)
        encrypted2 = service.encrypt(plaintext)

        assert encrypted1 != encrypted2  # Different due to salt/nonce
        assert service.decrypt(encrypted1) == plaintext
        assert service.decrypt(encrypted2) == plaintext

    def test_decrypt_invalid_data(self, service):
        """Test decryption of invalid data."""
        with pytest.raises(DecryptionError):
            service.decrypt(b"invalid encrypted data")

    def test_tenant_isolation(self, runtime_key):
        """Test that different tenants produce different encrypted data."""
        tenant1 = uuid4()
        tenant2 = uuid4()

        service1 = TenantEncryptionService(tenant1, runtime_key)
        service2 = TenantEncryptionService(tenant2, runtime_key)

        plaintext = "sensitive data"
        encrypted1 = service1.encrypt(plaintext)
        encrypted2 = service2.encrypt(plaintext)

        # Different tenants should produce different encrypted data
        assert encrypted1 != encrypted2

        # Each service should only decrypt its own data
        assert service1.decrypt(encrypted1) == plaintext
        assert service2.decrypt(encrypted2) == plaintext

        # Cross-tenant decryption should fail
        with pytest.raises(DecryptionError):
            service1.decrypt(encrypted2)
        with pytest.raises(DecryptionError):
            service2.decrypt(encrypted1)


class TestEncryptionServiceManager:
    """Test encryption service manager."""

    @pytest.fixture
    def runtime_key(self):
        """Generate test runtime key."""
        return EncryptionServiceManager.generate_runtime_key()

    @pytest.fixture
    def manager(self, runtime_key):
        """Create test service manager."""
        return EncryptionServiceManager(runtime_key)

    def test_generate_runtime_key(self):
        """Test runtime key generation."""
        key = EncryptionServiceManager.generate_runtime_key()
        assert isinstance(key, bytes)
        assert len(key) == 32

        # Should generate different keys
        key2 = EncryptionServiceManager.generate_runtime_key()
        assert key != key2

    def test_get_service(self, manager):
        """Test getting encryption service for tenant."""
        tenant_id = uuid4()

        service1 = manager.get_service(tenant_id)
        service2 = manager.get_service(tenant_id)

        assert service1 is service2  # Should return same instance
        assert service1.tenant_id == tenant_id

    def test_multiple_tenants(self, manager):
        """Test managing multiple tenant services."""
        tenant1 = uuid4()
        tenant2 = uuid4()

        service1 = manager.get_service(tenant1)
        service2 = manager.get_service(tenant2)

        assert service1 is not service2
        assert service1.tenant_id == tenant1
        assert service2.tenant_id == tenant2
