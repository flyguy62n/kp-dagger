"""
Tenant model for multi-tenant support.

This module defines the Tenant model that serves as the foundation
for multi-tenant data isolation in PyBastion.
"""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from pybastion.utils.get_timestamp import get_iso_timestamp


class Tenant(SQLModel, table=True):
    """
    Tenant model - source of truth for all tenant data.

    This table serves as the foundation for multi-tenant data isolation
    and enables clean tenant data operations like bulk deletion.
    """

    __tablename__ = "tenants"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the tenant",
    )

    name: str = Field(
        description="Tenant organization name",
    )

    slug: str = Field(
        unique=True,
        description="URL-safe tenant identifier (e.g., 'acme-corp')",
    )

    is_active: bool = Field(
        default=True,
        description="Whether this tenant is currently active",
    )

    created_at: datetime = Field(
        default_factory=get_iso_timestamp,
        description="Timestamp when the tenant was created",
    )

    updated_at: datetime = Field(
        default_factory=get_iso_timestamp,
        description="Timestamp when the tenant was last updated",
    )

    # Tenant-specific metadata
    description: str | None = Field(
        default=None,
        description="Optional description of the tenant",
    )

    contact_email: str | None = Field(
        default=None,
        description="Primary contact email for this tenant",
    )

    # Modern Pydantic v2 configuration
    model_config = ConfigDict(
        # Validate data when fields are modified after model creation
        validate_assignment=True,
        # Serialize enums as their values, not enum objects
        use_enum_values=True,
        # Add example data to JSON schema for API documentation
        json_schema_extra={
            "example": {
                "id": "456e7890-e89b-12d3-a456-426614174000",
                "name": "Acme Corporation",
                "slug": "acme-corp",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "description": "Large enterprise tenant",
                "contact_email": "admin@acme.com",
            },
        },
    )
