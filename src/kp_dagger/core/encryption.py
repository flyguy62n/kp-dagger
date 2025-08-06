"""
Core encryption service for Dagger.

Provides field-level encryption using AES256-GCM with tenant-specific
key derivation using Argon2id KDF. All encryption is performed with
authenticated encryption to ensure data integrity.
"""

import os
import secrets
from uuid import UUID

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    from argon2 import PasswordHasher
    from argon2.low_level import Type, hash_secret_raw

    HAS_ARGON2 = True
except ImportError:
    HAS_ARGON2 = False

# Constants
MIN_RUNTIME_KEY_LENGTH = 32
PBKDF2_ITERATIONS = 600000
GCM_NONCE_LENGTH = 12


class EncryptionError(Exception):
    """Base exception for encryption-related errors."""


class EncryptionConfigError(EncryptionError):
    """Raised when encryption configuration is invalid."""


class DecryptionError(EncryptionError):
    """Raised when decryption fails."""


class KDFConfig:
    """Configuration for key derivation functions."""

    def __init__(  # noqa: PLR0913
        self,
        algorithm: str = "argon2id",
        time_cost: int = 3,
        memory_cost: int = 65536,  # 64 MB
        parallelism: int = 1,
        salt_length: int = 32,
        key_length: int = 32,
    ) -> None:
        """
        Initialize KDF configuration.

        Args:
            algorithm: KDF algorithm ("argon2id" or "pbkdf2")
            time_cost: Time cost parameter for Argon2
            memory_cost: Memory cost parameter for Argon2 (in KB)
            parallelism: Parallelism parameter for Argon2
            salt_length: Salt length in bytes
            key_length: Derived key length in bytes

        """
        self.algorithm = algorithm
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.salt_length = salt_length
        self.key_length = key_length

        if algorithm == "argon2id" and not HAS_ARGON2:
            msg = "argon2-cffi library is required for Argon2id support"
            raise EncryptionConfigError(msg)


class TenantEncryptionService:
    """
    Tenant-specific encryption service using AES256-GCM with Argon2id KDF.

    This service provides field-level encryption for sensitive data with
    tenant isolation through tenant-specific key derivation.
    """

    def __init__(
        self,
        tenant_id: UUID,
        runtime_key: bytes,
        kdf_config: KDFConfig | None = None,
    ) -> None:
        """
        Initialize encryption service for a specific tenant.

        Args:
            tenant_id: UUID of the tenant
            runtime_key: Runtime key for additional entropy
            kdf_config: KDF configuration (uses defaults if not provided)

        """
        self.tenant_id = tenant_id
        self.runtime_key = runtime_key
        self.kdf_config = kdf_config or KDFConfig()

        if len(runtime_key) < MIN_RUNTIME_KEY_LENGTH:
            msg = f"Runtime key must be at least {MIN_RUNTIME_KEY_LENGTH} bytes"
            raise EncryptionConfigError(msg)

    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive encryption key using configured KDF.

        Args:
            salt: Salt for key derivation

        Returns:
            Derived encryption key

        """
        # Combine tenant ID and runtime key for key material
        key_material = str(self.tenant_id).encode() + self.runtime_key

        if self.kdf_config.algorithm == "argon2id":
            return self._derive_key_argon2(key_material, salt)
        if self.kdf_config.algorithm == "pbkdf2":
            return self._derive_key_pbkdf2(key_material, salt)

        msg = f"Unsupported KDF: {self.kdf_config.algorithm}"
        raise EncryptionConfigError(msg)

    def _derive_key_argon2(self, key_material: bytes, salt: bytes) -> bytes:
        """Derive key using Argon2id."""
        return hash_secret_raw(
            secret=key_material,
            salt=salt,
            time_cost=self.kdf_config.time_cost,
            memory_cost=self.kdf_config.memory_cost,
            parallelism=self.kdf_config.parallelism,
            hash_len=self.kdf_config.key_length,
            type=Type.ID,
        )

    def _derive_key_pbkdf2(self, key_material: bytes, salt: bytes) -> bytes:
        """Derive key using PBKDF2 (fallback when Argon2 unavailable)."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.kdf_config.key_length,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
            backend=default_backend(),
        )
        return kdf.derive(key_material)

    def encrypt(self, plaintext: str) -> bytes:
        """
        Encrypt plaintext string.

        Args:
            plaintext: String to encrypt

        Returns:
            Encrypted data (salt + nonce + ciphertext + tag)

        """
        if not plaintext:
            return b""

        # Generate salt and nonce
        salt = os.urandom(self.kdf_config.salt_length)
        nonce = os.urandom(GCM_NONCE_LENGTH)

        # Derive encryption key
        key = self._derive_key(salt)

        # Encrypt with AES-GCM
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

        # Return: salt + nonce + ciphertext (includes tag)
        return salt + nonce + ciphertext

    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Decrypt encrypted data.

        Args:
            encrypted_data: Encrypted data from encrypt()

        Returns:
            Decrypted plaintext string

        """
        if not encrypted_data:
            return ""

        try:
            # Extract components
            salt_len = self.kdf_config.salt_length
            salt = encrypted_data[:salt_len]
            nonce = encrypted_data[salt_len : salt_len + GCM_NONCE_LENGTH]
            ciphertext = encrypted_data[salt_len + GCM_NONCE_LENGTH :]

            # Derive decryption key
            key = self._derive_key(salt)

            # Decrypt with AES-GCM
            aesgcm = AESGCM(key)
            plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)

            return plaintext_bytes.decode("utf-8")

        except Exception as e:
            msg = f"Failed to decrypt data: {e}"
            raise DecryptionError(msg) from e


class EncryptionServiceManager:
    """Manages encryption services for multiple tenants."""

    def __init__(self, runtime_key: bytes, kdf_config: KDFConfig | None = None) -> None:
        """
        Initialize the encryption service manager.

        Args:
            runtime_key: Runtime key for all tenants
            kdf_config: KDF configuration

        """
        self.runtime_key = runtime_key
        self.kdf_config = kdf_config or KDFConfig()
        self._services: dict[UUID, TenantEncryptionService] = {}

    def get_service(self, tenant_id: UUID) -> TenantEncryptionService:
        """Get or create encryption service for tenant."""
        if tenant_id not in self._services:
            self._services[tenant_id] = TenantEncryptionService(
                tenant_id=tenant_id,
                runtime_key=self.runtime_key,
                kdf_config=self.kdf_config,
            )
        return self._services[tenant_id]

    @classmethod
    def generate_runtime_key(cls) -> bytes:
        """Generate a secure runtime key."""
        return secrets.token_bytes(MIN_RUNTIME_KEY_LENGTH)
