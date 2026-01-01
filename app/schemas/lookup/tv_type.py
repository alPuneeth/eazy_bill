from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated
from datetime import datetime

NonEmptyStr = Annotated[
                str,
                StringConstraints(
                    strip_whitespace=True,
                    min_length=1,
                    max_length=100
                        )]


class TVTypeCreate(BaseModel):
    name: NonEmptyStr = Field(
        title="TV Type",
        description="Type of television technology",

        json_schema_extra={
            "examples": ["LED", "LCD", "OLED"]
        }
        )
    description: Optional[str] = Field(
        default=None
        )


class TVTypeRead(BaseModel):
    model_config = {
        "from_attributes": True
        }

    id: int
    name: str
    description: Optional[str] = Field(
        default=None
        )
    created_at: datetime
    updated_at: datetime


class TVTypeUpdate(BaseModel):
    name: Optional[NonEmptyStr] = Field(
        default=None
        )
    description: Optional[str] = Field(
        default=None
        )
