from pydantic import BaseModel


class IdValueRead(BaseModel):
    id: int
    value: str


class VillageSummary(BaseModel):
    id: int
    name: str
    village_code: str


class CreatorSummary(BaseModel):
    public_id: str
    name: str