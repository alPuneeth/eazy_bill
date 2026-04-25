import uuid
import random
import string

from app.models.core_models.customer import Customer


def create_customer(
    session,
    village_id,
    customer_type_id,
    ftth64_id,
    package_id,
    name=None,
    phone=None,
):
    """
    Minimal DB-level customer factory.
    Does NOT handle device info or business logic.
    """

    phone = phone or "".join(random.choices(string.digits, k=10))
    name = name or f"TestCustomer_{random.randint(100, 999)}"

    customer = Customer(
        public_id=str(uuid.uuid4()),
        name=name,
        phone=phone,
        village_id=village_id,
        customer_type_id=customer_type_id,
        ftth64_id=ftth64_id,
        package_id=package_id,
    )

    session.add(customer)
    session.flush()

    return customer