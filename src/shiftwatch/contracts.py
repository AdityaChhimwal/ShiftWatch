"""Small draft request schemas; these do not attach labels or measure error."""

from pydantic import BaseModel, ConfigDict, Field


class LabelRecord(BaseModel):
    """Validate one label's shape before any prediction lookup or storage."""

    model_config = ConfigDict(strict=True, extra="forbid")

    # A draft application-ID rule, not a claim about a source dataset column.
    record_id: str = Field(min_length=1, max_length=64, pattern=r"^\S+$")
    cnt: int = Field(ge=0)
