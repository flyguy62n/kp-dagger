"""
Base model for PyBastion application.

This module defines the PyBastionBaseModel that serves as the foundation
for all other SQLModel-based models in the application.
"""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from pybastion.utils.get_timestamp import get_timestamp


class PyBastionBaseModel(SQLModel):
    """
    Base model class for all PyBastion application models.

    This class provides common fields and functionality that should be
    inherited by all other models in the application. It includes:

    - id: UUID primary key for unique identification
    - created_at: Timestamp of record creation
    - updated_at: Timestamp of last update

    The model is designed to work with DuckDB and follows SQLModel patterns
    for both Pydantic validation and SQLAlchemy ORM functionality.
    """

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the record",
    )

    created_at: datetime = Field(
        default_factory=get_timestamp,
        description="Timestamp when the record was created",
    )

    updated_at: datetime = Field(
        default_factory=get_timestamp,
        description="Timestamp when the record was last updated",
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
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        },
    )
