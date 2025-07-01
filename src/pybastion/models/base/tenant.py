"""
Tenant model for multi-tenant support.

This module defines the Tenant model that serves as the foundation
for multi-tenant data isolation in PyBastion.
"""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlmodel import Field

from pybastion.models.base.base import PyBastionConfigMixin
from pybastion.utils.get_timestamp import get_iso_timestamp


class Tenant(PyBastionConfigMixin, table=True):
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
        max_length=255,
        description="Tenant organization name",
    )

    slug: str = Field(
        unique=True,
        max_length=100,
        regex=r"^[a-z0-9-]+$",  # Only lowercase, numbers, hyphens
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
        max_length=1000,
        description="Optional description of the tenant",
    )

    # Technical settings
    timezone: str = Field(
        default="UTC",
        max_length=50,
        description="Timezone for this tenant (used for timestamp generation)",
    )

    retention_policy_days: int = Field(
        default=0,
        description="Data retention policy in days (0 = forever)",
    )

    # Configuration extending base settings with tenant-specific examples
    model_config = PyBastionConfigMixin.model_config | ConfigDict(
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
                "timezone": "UTC",
                "retention_policy_days": 0,
            },
        },
    )

    @classmethod
    def generate_slug_from_name(cls, name: str) -> str:
        """
        Generate a URL-safe slug from a tenant name.

        Args:
            name: The tenant name to convert

        Returns:
            A URL-safe slug

        Example:
            >>> Tenant.generate_slug_from_name("ACME Corporation")
            'acme-corporation'

        """
        import re

        # Convert to lowercase, replace spaces/special chars with hyphens
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower())
        # Remove leading/trailing hyphens and collapse multiple hyphens
        slug = re.sub(r"^-+|-+$", "", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = get_iso_timestamp()
