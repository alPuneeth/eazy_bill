# standard library
from typing import TYPE_CHECKING, Optional

# third-party
from sqlmodel import SQLModel, Field, Relationship

# local module
from app.models.utilities import TimestampMixin

if TYPE_CHECKING:
    from app.models.devices.device_info import DeviceInfo


class TVType(TimestampMixin, SQLModel, table=True):
    """
    TVType represents the type or technology of a television
    device, such as LED, LCD, OLED, etc.

    This model acts as a canonical lookup table where each
    TV type exists exactly once, enforced by a unique constraint
    on the name field.

    The model defines database structure only.
    Any classification or validation logic is handled at the
    application or service layer.

    """

    id: Optional[int] = Field(
        default=None,
        primary_key=True
        )

    name: str = Field(
        ...,
        nullable=False,
        unique=True,
        min_length=1,
        max_length=100
        )

    description: Optional[str] = Field(
        nullable=True,
        default=None
        )
    devices: list["DeviceInfo"] = Relationship(
        back_populates="tvtype"
        )
