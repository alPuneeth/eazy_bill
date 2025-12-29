from pydantic import BaseModel, ConfigDict


class VillageCustomerStatusSummary(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

    village_name: str
    active_count: int
    inactive_count: int
    total_count: int
