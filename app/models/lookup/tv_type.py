# standard library
from typing import Optional

# third-party
from sqlmodel import SQLModel, Field

# local module
from app.models.utilities import TimestampMixin


class TVType(TimestampMixin, SQLModel, table=True):
    """
    TVType represents the type or technology of a television
    device, such as LED, LCD, OLED, etc.

    This model is descriptive in nature and may contain multiple
    rows with the same name if required (for example, variations
    across vendors or contexts). It is not a canonical lookup
    table enforcing one row per value.

    The model defines database structure only.
    Any normalization or reuse decisions are handled at the
    application or data-management level.

    """

    id: Optional[int] = Field(
        default=None,
        primary_key=True
        )

    name: str = Field(
        ...,
        nullable=False,
        index=True
        )

    description: Optional[str] = Field(
        nullable=True,
        default=None
        )