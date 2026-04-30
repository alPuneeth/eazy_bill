from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated
from datetime import datetime

NameStr = Annotated[
                str,
                StringConstraints(
                    strip_whitespace=True,
                    max_length=100,
                    to_lower=True,
                    min_length=1
                        )]


class TVTypeCreate(BaseModel):
    name: NameStr = Field(
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
    name: Optional[NameStr] = Field(
        default=None
        )
    description: Optional[str] = Field(
        default=None
        )
