"""Parser configuration models for Dagger application."""

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class ParserConfig(BaseModel):
    """Configuration for individual device parsers."""

    enabled: bool = True
    module: str = Field(..., min_length=1)
    class_name: str = Field(..., alias="class", min_length=1)
    cleaner: str = Field(..., min_length=1)
    description: str | None = None

    @classmethod
    @field_validator("module")
    def validate_module_path(cls, v: str) -> str:
        """Validate module path format."""
        if not v.startswith("kp_dagger.parsers."):
            msg = "Parser module must be within kp_dagger.parsers package"
            raise ValueError(msg)
        return v

    @classmethod
    @field_validator("class_name")
    def validate_class_name(cls, v: str) -> str:
        """Validate class name format."""
        if not v.endswith("Parser"):
            msg = 'Parser class name must end with "Parser"'
            raise ValueError(msg)
        return v

    @classmethod
    @field_validator("cleaner")
    def validate_cleaner_name(cls, v: str) -> str:
        """Validate cleaner class name format."""
        if not v.endswith("Cleaner"):
            msg = 'Cleaner class name must end with "Cleaner"'
            raise ValueError(msg)
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )
