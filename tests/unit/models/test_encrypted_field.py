"""Unit tests for the encrypted field descriptor."""

from uuid import uuid4

import pytest
from sqlmodel import Field

from pybastion.core.encryption import EncryptionServiceManager, TenantEncryptionService
from pybastion.models.base.base import PyBastionBaseModel
from pybastion.models.base.encryption import EncryptedField


class TestModel(PyBastionBaseModel, table=True):
    """Test model with encrypted field."""

    __tablename__ = "test_models"

    # Encrypted field
    secret_data: str = EncryptedField("secret_data_encrypted")
    secret_data_encrypted: bytes | None = Field(default=None, exclude=True)

    # Optional encrypted field
    optional_secret: str = EncryptedField("optional_secret_encrypted", nullable=True)
    optional_secret_encrypted: bytes | None = Field(default=None, exclude=True)


class TestEncryptedField:
    """Test encrypted field descriptor."""

    @pytest.fixture
    def encryption_service(self) -> TenantEncryptionService:
        """Create test encryption service."""
        tenant_id = uuid4()
        runtime_key = EncryptionServiceManager.generate_runtime_key()
        return TenantEncryptionService(tenant_id, runtime_key)

    @pytest.fixture
    def test_instance(self, encryption_service: TenantEncryptionService) -> TestModel:
        """Create test model instance with encryption service."""
        instance = TestModel(tenant_id=uuid4())
        instance.set_encryption_service(encryption_service)
        return instance

    def test_set_and_get_encrypted_field(self, test_instance: TestModel) -> None:
        """Test setting and getting encrypted field value."""
        secret_value = "super secret data"

        # Set the value
        test_instance.secret_data = secret_value

        # Check that storage field contains encrypted data
        assert test_instance.secret_data_encrypted is not None
        assert isinstance(test_instance.secret_data_encrypted, bytes)
        assert test_instance.secret_data_encrypted != secret_value.encode()

        # Check that we can retrieve the decrypted value
        assert test_instance.secret_data == secret_value

    def test_set_none_nullable_field(self, test_instance: TestModel) -> None:
        """Test setting None on nullable field."""
        test_instance.optional_secret = None

        assert test_instance.optional_secret is None
        assert test_instance.optional_secret_encrypted is None

    def test_set_none_non_nullable_field(self, test_instance: TestModel) -> None:
        """Test setting None on non-nullable field raises error."""
        with pytest.raises(ValueError, match="cannot be None"):
            test_instance.secret_data = None

    def test_caching_behavior(self, test_instance: TestModel) -> None:
        """Test that decrypted values are cached."""
        secret_value = "cached secret"

        # Set value
        test_instance.secret_data = secret_value

        # Access multiple times
        value1 = test_instance.secret_data
        value2 = test_instance.secret_data

        assert value1 == secret_value
        assert value2 == secret_value

    def test_without_encryption_service(self) -> None:
        """Test that accessing encrypted field without service raises error."""
        instance = TestModel(tenant_id=uuid4())

        with pytest.raises(RuntimeError, match="Encryption service not available"):
            instance.secret_data = "test"

        # Set encrypted data directly for get test
        instance.secret_data_encrypted = b"some encrypted data"

        with pytest.raises(RuntimeError, match="Encryption service not available"):
            _ = instance.secret_data

    def test_corrupted_data_handling(self, test_instance: TestModel) -> None:
        """Test that corrupted encrypted data returns None."""
        # Set invalid encrypted data
        test_instance.secret_data_encrypted = b"corrupted data"

        # Should return None instead of raising exception
        assert test_instance.secret_data is None

    def test_model_dump_encrypted(self, test_instance: TestModel) -> None:
        """Test dumping model with encrypted fields."""
        test_instance.secret_data = "secret value"
        test_instance.optional_secret = "optional secret"

        # Dump with encrypted fields
        data = test_instance.model_dump_encrypted()

        # Should contain basic fields
        assert "id" in data
        assert "tenant_id" in data
        assert "created_at" in data
        assert "updated_at" in data
