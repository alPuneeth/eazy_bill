from pydantic import BaseModel


class IdValueRead(BaseModel):
    id: int
    value: str
