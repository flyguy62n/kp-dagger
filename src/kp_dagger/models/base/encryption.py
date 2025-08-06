"""
Encryption field descriptor for SQLModel integration.

Provides transparent field-level encryption for SQLModel models using
the TenantEncryptionService.
"""

from kp_dagger.core.encryption import DecryptionError


class EncryptedField:
    """
    Descriptor for transparent field-level encryption in SQLModel models.

    This descriptor automatically encrypts data when setting field values
    and decrypts when retrieving them, providing transparent encryption
    for sensitive model fields.
    """

    def __init__(self, storage_field: str, *, nullable: bool = True) -> None:
        """
        Initialize the encrypted field descriptor.

        Args:
            storage_field: Name of the underlying storage field (with _encrypted suffix)
            nullable: Whether the field can be None

        """
        self.storage_field = storage_field
        self.nullable = nullable

    def __set_name__(self, owner: type, name: str) -> None:
        """Set the attribute name when the descriptor is assigned to a class."""
        self.name = name
        self.private_name = f"_{name}"

    def __get__(
        self,
        obj: "KPDaggerBaseModel | None",
        objtype: type | None = None,
    ) -> str | None:
        """Get the decrypted field value."""
        if obj is None:
            return self

        # Check if we have a cached decrypted value
        if hasattr(obj, self.private_name):
            return getattr(obj, self.private_name)

        # Get encrypted data from storage field
        encrypted_data = getattr(obj, self.storage_field, None)
        if encrypted_data is None:
            return None

        # Decrypt the data
        encryption_service = getattr(obj, "_encryption_service", None)
        if encryption_service is None:
            msg = "Encryption service not available for decryption"
            raise RuntimeError(msg)

        try:
            decrypted_value = encryption_service.decrypt(encrypted_data)
            # Cache the decrypted value
            setattr(obj, self.private_name, decrypted_value)
        except DecryptionError:
            # Return None for corrupted data instead of raising
            return None
        else:
            return decrypted_value

    def __set__(self, obj: "KPDaggerBaseModel", value: str | None) -> None:
        """Set the field value with encryption."""
        if value is None and self.nullable:
            setattr(obj, self.storage_field, None)
            setattr(obj, self.private_name, None)
            return

        if value is None and not self.nullable:
            msg = f"Field {self.name} cannot be None"
            raise ValueError(msg)

        # Encrypt the value
        encryption_service = getattr(obj, "_encryption_service", None)
        if encryption_service is None:
            msg = "Encryption service not available for encryption"
            raise RuntimeError(msg)

        encrypted_data = encryption_service.encrypt(str(value))
        setattr(obj, self.storage_field, encrypted_data)
        # Cache the plaintext value
        setattr(obj, self.private_name, value)

    def __delete__(self, obj: "KPDaggerBaseModel") -> None:
        """Delete the field value."""
        setattr(obj, self.storage_field, None)
        if hasattr(obj, self.private_name):
            delattr(obj, self.private_name)
