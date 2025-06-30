"""
Customer model for multi-tenant support.

This module defines the Customer model that serves as the foundation
for multi-tenant data isolation in PyBastion.
"""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from pybastion.utils.get_timestamp import get_iso_timestamp


class Customer(SQLModel, table=True):
    """
    Customer/tenant model - source of truth for all customer data.

    This table serves as the foundation for multi-tenant data isolation
    and enables clean customer data operations like bulk deletion.
    """

    __tablename__ = "customers"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the customer",
    )

    name: str = Field(
        description="Customer organization name",
    )

    slug: str = Field(
        unique=True,
        description="URL-safe customer identifier (e.g., 'acme-corp')",
    )

    is_active: bool = Field(
        default=True,
        description="Whether this customer is currently active",
    )

    created_at: datetime = Field(
        default_factory=get_iso_timestamp,
        description="Timestamp when the customer was created",
    )

    updated_at: datetime = Field(
        default_factory=get_iso_timestamp,
        description="Timestamp when the customer was last updated",
    )

    # Customer-specific metadata
    description: str | None = Field(
        default=None,
        description="Optional description of the customer",
    )

    contact_email: str | None = Field(
        default=None,
        description="Primary contact email for this customer",
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
                "description": "Large enterprise customer",
                "contact_email": "admin@acme.com",
            },
        },
    )
