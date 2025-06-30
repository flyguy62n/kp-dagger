"""
Base model for PyBastion application.

This module defines the PyBastionBaseModel that serves as the foundation
for all other SQLModel-based models in the application.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from pybastion.utils.get_timestamp import get_iso_timestamp

if TYPE_CHECKING:
    from pybastion.core.encryption import TenantEncryptionService


class PyBastionBaseModel(SQLModel):
    """
    Base model class for all PyBastion application models with multi-tenant support.

    This class provides common fields and functionality that should be
    inherited by all other models in the application. It includes:

    - id: UUID primary key for unique identification
    - tenant_id: Foreign key reference to tenants table for multi-tenancy
    - created_at: Timestamp of record creation
    - updated_at: Timestamp of last update
    - Encryption service support for field-level encryption

    The model is designed to work with DuckDB and follows SQLModel patterns
    for both Pydantic validation and SQLAlchemy ORM functionality.
    """

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the record",
    )

    tenant_id: UUID = Field(
        foreign_key="tenants.id",
        description="Tenant this record belongs to",
        index=True,
    )

    created_at: datetime = Field(
        default_factory=get_iso_timestamp,
        description="Timestamp when the record was created",
    )

    updated_at: datetime = Field(
        default_factory=get_iso_timestamp,
        description="Timestamp when the record was last updated",
    )

    # Modern Pydantic v2 configuration
    model_config = ConfigDict(
        # Validate data when fields are modified after model creation
        validate_assignment=True,
        # Serialize enums as their values, not enum objects
        use_enum_values=True,
        # Allow arbitrary types for encryption service and descriptors
        arbitrary_types_allowed=True,
        # Ignore descriptor types
        ignored_types=(property,),
        # Add example data to JSON schema for API documentation
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "tenant_id": "456e7890-e89b-12d3-a456-426614174000",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        },
    )

    def __init__(self, **data: object) -> None:
        """Initialize model with optional encryption service."""
        # Extract encryption service if provided
        self._encryption_service: TenantEncryptionService | None = data.pop(
            "_encryption_service",
            None,
        )
        super().__init__(**data)

    def set_encryption_service(self, service: "TenantEncryptionService") -> None:
        """Set the encryption service for this model instance."""
        self._encryption_service = service

    def model_dump_encrypted(self) -> dict[str, object]:
        """
        Dump model data with encrypted fields in their encrypted form.

        This is useful for database storage where encrypted fields should
        remain encrypted.
        """
        data = {}
        for field_name in self.model_fields:
            if hasattr(self.__class__, field_name):
                attr = getattr(self.__class__, field_name)
                if isinstance(
                    attr, type(self).__dict__.get(field_name, None)
                ) and hasattr(attr, "storage_field"):
                    # This is an EncryptedField, get the storage field
                    storage_value = getattr(self, attr.storage_field, None)
                    data[attr.storage_field] = storage_value
                    continue

            # Regular field
            data[field_name] = getattr(self, field_name, None)

        return data
