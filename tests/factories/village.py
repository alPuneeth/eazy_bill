import uuid

from sqlalchemy.exc import IntegrityError

from app.models.lookup.village import Village


def create_village(
        session,
        name=None,
        code=None,
        postal="577000",
        agent=None
        ):
    """
    Create and persist a test village in the database.

    Optionally assigns it to an agent to simulate ownership.
    Returns the created village instance.
    """

    name = name or f"Village-{uuid.uuid4().hex[:6]}"
    code = code or uuid.uuid4().hex[:6].upper()

    for _ in range(5):
        try:
            with session.begin_nested():

                village = Village(
                    name=name,
                    postal_code=postal,
                    village_code=code,
                    agent=agent
                )

                session.add(village)
                session.flush()

                return village

        except IntegrityError:
            # regenerate only conflicting fields
            code = uuid.uuid4().hex[:6].upper()
            name = f"Village-{uuid.uuid4().hex[:6]}"

    raise RuntimeError("Failed to create unique village")