from sqlmodel import Session, select

from app.models.lookup.village import Village
from app.services.bill.bill_exceptions import VillageNotFoundError

def get_village_by_code_or_fail(session: Session, village_code: str):
    village = session.exec(
        select(Village).where(Village.village_code == village_code)
    ).first()

    if not village:
        raise VillageNotFoundError()

    return village