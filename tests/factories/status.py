from sqlmodel import select

from app.models.lookup.status import Status, StatusEnum


def create_status(session, name):
    existing = session.exec(
        select(Status).where(Status.name == name)
    ).first()
    if existing:
        return existing

    obj = Status(name=name)
    session.add(obj)
    session.flush()
    return obj

