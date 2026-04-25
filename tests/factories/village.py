import random
import string

from app.models.lookup.village import Village


def create_village(
        session,
        name=None,
        village_code=None,
        postal_code=None
        ):
    """
    Create a valid village for tests.
    """

    name = name or "Village_" + "".join(random.choices(string.ascii_uppercase, k=5))
    postal_code = postal_code or "".join(random.choices(string.digits, k=6))
    village_code = village_code or "VC_" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

    village = Village(
        name=name,
        postal_code=postal_code,
        village_code=village_code
    )

    session.add(village)
    session.flush()

    return village