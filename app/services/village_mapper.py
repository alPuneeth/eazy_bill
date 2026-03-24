from app.schemas.village import VillageRead
from app.models.lookup.village import Village


def to_village_read(v:Village) -> VillageRead:
    return VillageRead(
            id=v.id,
            name=v.name,
            postal_code=v.postal_code,
            village_code=v.village_code,
            agent_public_id=v.agent.public_id if v.agent else None,
            created_at=v.created_at,
            updated_at=v.updated_at
    )