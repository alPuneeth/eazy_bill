import uuid

from sqlmodel import select

from app.models.core_models.customer import Customer
from tests.factories.status import create_status
from tests.factories.village import create_village
from tests.factories.package import create_package
from tests.factories.customer import create_customer, create_customer_type
from app.models.lookup.customer_type import CustomerTypeEnum
from app.models.lookup.ftth64 import FTTH64
from app.models.devices.device_info import DeviceInfo


def test_create_customer_success(client, session):
    """
    Verify that a customer is created successfully.
    """
    # --- setup lookup data ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    status = create_status(session)

    ftth64 = FTTH64(
        name="FTTH-TEST"
    )
    session.add(ftth64)

    session.commit()

    # --- request payload ---
    payload = {
        "name": "Test Customer",
        "phone": "9999999998",
        "status_id": status.id,
        "vc_number": "VC123456",
        "village_id": village.id,
        "customer_type_id": customer_type.id,
        "ftth64_id": ftth64.id,
        "package_id": package.id
    }

    # API call
    response = client.post("/customer/", json=payload)
    data = response.json()

    # assertions
    assert response.status_code == 200
    assert data["name"] == payload["name"]
    assert data["phone"] == payload["phone"]
    assert data["vc_number"] == payload["vc_number"]

    # --- DB verification ---
    from sqlmodel import select
    from app.models.core_models.customer import Customer

    customer = session.exec(
        select(Customer).where(Customer.phone == payload["phone"])
    ).first()

    assert customer is not None
    assert customer.name == payload["name"] 

    device = session.exec(
        select(DeviceInfo).where(DeviceInfo.vc_number == payload["vc_number"])
    ).first()

    assert device is not None
    assert device.status_id == status.id
    assert device.customer_id == customer.id


def test_get_customer_success(client, session):
    """
    Verify that a customer can be fetched by public_id.
    """
    # --- setup ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    status = create_status(session)

    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.flush()

    customer = create_customer(
        session,
        village_id=village.id,
        customer_type_id=customer_type.id,
        ftth64_id=ftth64.id,
        package_id=package.id,
        phone="9999999997"
    )

    device = DeviceInfo(
        public_id=str(uuid.uuid4()),
        customer_id=customer.id,
        vc_number="VC999",
        status_id=status.id
    )

    session.add(device)
    session.commit()

    # --- API call ---
    response = client.get(f"/customer/{customer.public_id}")
    data = response.json()

    # --- assertions ---
    assert response.status_code == 200
    assert data["public_id"] == customer.public_id
    assert data["name"] == customer.name
    assert data["phone"] == customer.phone
    assert data["vc_number"] == "VC999"


def test_get_customer_not_found(client):
    """
    Verify 404 when customer does not exist.
    """
    response = client.get("/customer/non-existent-id")

    assert response.status_code == 404


def test_list_customers_success(client, session):
    """
    Verify that list_customers returns paginated active/inactive customers.
    """
    # --- setup ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    status = create_status(session)  # ACTIVE

    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.flush()

    customers = []

    for i in range(3):
        customer = create_customer(
            session,
            village_id=village.id,
            customer_type_id=customer_type.id,
            ftth64_id=ftth64.id,
            package_id=package.id,
            phone=f"99999999{i}"
        )

        device = DeviceInfo(
            public_id=str(uuid.uuid4()),
            customer_id=customer.id,
            vc_number=f"VC{i}",
            status_id=status.id
        )
        session.add(device)

        customers.append(customer)

    session.commit()

    # --- API call ---
    response = client.get("/customer/?page=1&page_size=10")
    data = response.json()

    # --- assertions ---
    assert response.status_code == 200
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) == 3

    returned_ids = {c["public_id"] for c in data["items"]}
    expected_ids = {c.public_id for c in customers}

    assert returned_ids == expected_ids


def test_list_customers_empty(client):
    """
    Verify empty response when no customers exist.
    """

    response = client.get("/customer/?page=1&page_size=10")
    data = response.json()

    assert response.status_code == 200
    assert data["total"] == 0
    assert data["items"] == []


def test_update_customer_success(client, session):
    """
    Verify that a customer can be updated successfully.
    """

    # --- setup ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    status = create_status(session)

    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.flush()

    customer = create_customer(
        session,
        village_id=village.id,
        customer_type_id=customer_type.id,
        ftth64_id=ftth64.id,
        package_id=package.id,
        phone="9999999911",
        name="Old Name"
    )

    device = DeviceInfo(
        public_id=str(uuid.uuid4()),
        customer_id=customer.id,
        vc_number="VC111",
        status_id=status.id
    )
    session.add(device)

    session.commit()

    # --- update payload ---
    payload = {
        "name": "Updated Name",
        "phone": "9999999922"
    }

    # --- API call ---
    response = client.patch(f"/customer/{customer.public_id}", json=payload)
    data = response.json()

    # --- assertions ---
    assert response.status_code == 200
    assert data["name"] == "Updated Name"
    assert data["phone"] == "9999999922"

    # --- DB verification ---
    updated_customer = session.exec(
        select(Customer).where(Customer.id == customer.id)
    ).first()

    assert updated_customer.name == "Updated Name"
    assert updated_customer.phone == "9999999922"


def test_update_customer_not_found(client):
    """
    Verify 404 when updating non-existent customer.
    """

    payload = {"name": "Does not matter"}

    response = client.patch("/customer/non-existent-id", json=payload)

    assert response.status_code == 404


def test_create_customers_bulk_success(client, session):
    """
    Verify bulk onboarding succeeds for valid customers.
    """
    # --- setup ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    status = create_status(session)

    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.commit()

    payload = {
        "customers": [
            {
                "name": "User1",
                "phone": "9000000001",
                "vc_number": "VCB1",
                "status_id": status.id,
                "village_id": village.id,
                "customer_type_id": customer_type.id,
                "ftth64_id": ftth64.id,
                "package_id": package.id
            },
            {
                "name": "User2",
                "phone": "9000000002",
                "vc_number": "VCB2",
                "status_id": status.id,
                "village_id": village.id,
                "customer_type_id": customer_type.id,
                "ftth64_id": ftth64.id,
                "package_id": package.id
            }
        ]
    }

    response = client.post("/customer/bulk", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert len(data["success"]) == 2
    assert data["failed"] == []


def test_create_customers_bulk_partial_failure(client, session):
    """
    Verify that invalid entries fail while valid ones succeed.
    """

    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    status = create_status(session)

    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.commit()

    payload = {
        "customers": [
            {
                "name": "Valid User",
                "phone": "9000000003",
                "vc_number": "VCB3",
                "status_id": status.id,
                "village_id": village.id,
                "customer_type_id": customer_type.id,
                "ftth64_id": ftth64.id,
                "package_id": package.id
            },
            {
                # ❌ missing vc_number → validation error
                "name": "Invalid User",
                "phone": "9000000004",
                "status_id": status.id,
                "village_id": village.id,
                "customer_type_id": customer_type.id,
                "ftth64_id": ftth64.id,
                "package_id": package.id
            }
        ]
    }

    response = client.post("/customer/bulk", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert len(data["success"]) == 1
    assert len(data["failed"]) == 1


def test_create_customers_bulk_duplicate_phone(client, session):
    """
    Verify duplicate phone causes partial failure in bulk onboarding.
    """

    from tests.factories.village import create_village
    from tests.factories.package import create_package
    from tests.factories.customer import create_customer_type
    from tests.factories.status import create_status
    from app.models.lookup.customer_type import CustomerTypeEnum
    from app.models.lookup.ftth64 import FTTH64

    # --- setup ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    status = create_status(session)

    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.commit()

    # --- payload ---
    payload = {
        "customers": [
            {
                "name": "User1",
                "phone": "9000000010",
                "vc_number": "VCX1",
                "status_id": status.id,
                "village_id": village.id,
                "customer_type_id": customer_type.id,
                "ftth64_id": ftth64.id,
                "package_id": package.id
            },
            {
                # ❌ duplicate phone
                "name": "User2",
                "phone": "9000000010",
                "vc_number": "VCX2",
                "status_id": status.id,
                "village_id": village.id,
                "customer_type_id": customer_type.id,
                "ftth64_id": ftth64.id,
                "package_id": package.id
            }
        ]
    }

    # --- API call ---
    response = client.post("/customer/bulk", json=payload)
    data = response.json()

    # --- assertions ---
    assert response.status_code == 200
    assert len(data["success"]) == 1
    assert len(data["failed"]) == 1


