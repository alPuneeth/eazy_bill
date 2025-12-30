from sqlmodel import Session, select
from app.models.lookup.status import Status, StatusEnum


def get_active_inactive_status_ids(session: Session) -> tuple[int, int]:
    rows = session.exec(
        select(Status.id, Status.name)
        .where(Status.name.in_([StatusEnum.ACTIVE, StatusEnum.INACTIVE]))
    ).all()

    mapping = {name: id_ for id_, name in rows}
    return mapping[StatusEnum.ACTIVE], mapping[StatusEnum.INACTIVE]
