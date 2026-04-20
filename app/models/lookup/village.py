# Standard library
from typing import Optional

# Third-party
from sqlmodel import SQLModel, Field, Relationship

# Local application
from app.models.utilities import TimestampMixin
# from app.models.core_models.user import User
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.core_models.user import User


class Village(TimestampMixin, SQLModel, table=True):
    """
    Village represents a geographic locality used for customer
    classification and address association.

    This model stores standardized village identifiers along with
    human-readable names and postal codes. The village_code acts
    as a canonical, human-referenced identifier used in lookups,
    imports, and integrations.

    The model defines database structure and integrity only.
    Any address validation, formatting, or hierarchy logic
    is enforced at the application or service layer.

    """
    id: Optional[int] = Field(
        default=None,
        primary_key=True
        )

    # Human-readable village name, commonly used in search
    name: str = Field(
        ...,
        unique=True,
        index=True,
        nullable=False,
        max_length=100
        )

    # Postal / PIN code, frequently filtered
    postal_code: str = Field(
        ...,
        index=True,
        nullable=False,
        max_length=6
        )

    # Canonical human-referenced identifier
    village_code: str = Field(
        ...,
        unique=True,
        index=True,
        max_length=100,
        nullable=False
        )

    # ownership of village
    agent_id: Optional[int] = Field(
        foreign_key="user.id",
        index=True,
        default=None,
        nullable=True,
        description="Village belongs to this agent"
    )

    # relationship
    agent: Optional["User"] = Relationship(back_populates="villages")
