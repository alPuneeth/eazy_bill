import uuid

from sqlmodel import select

from app.core.security import create_access_token

from app.models.core_models.customer import Customer
from app.models.lookup.status import StatusEnum
from app.models.lookup.customer_type import CustomerTypeEnum
from app.models.lookup.ftth64 import FTTH64
from app.models.devices.device_info import DeviceInfo

from app.services.status_ids import get_active_inactive_status_ids

from tests.factories.status import create_status
from tests.factories.user import create_admin, create_agent
from tests.factories.village import create_village
from tests.factories.package import create_package
from tests.factories.customer import create_customer, create_customer_type


def test_create_customer_success(client, session):
    """
    Verify that a customer is created successfully.
    """
    # --- setup lookup data ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    active = create_status(session, StatusEnum.ACTIVE)
    inactive = create_status(session, StatusEnum.INACTIVE)

    _, inactive_status_id = get_active_inactive_status_ids(session)


    ftth64 = FTTH64(
        name="FTTH-TEST"
    )
    session.add(ftth64)

    session.commit()

    # --- request payload ---
    payload = {
        "name": "Test Customer",
        "phone": "9999999998",
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
    customer = session.exec(
        select(Customer).where(Customer.phone == payload["phone"])
    ).first()

    assert customer is not None
    assert customer.name == payload["name"] 

    device = session.exec(
        select(DeviceInfo).where(DeviceInfo.vc_number == payload["vc_number"])
    ).first()

    assert device is not None
    assert device.status_id == inactive_status_id
    assert device.customer_id == customer.id


def test_create_customer_duplicate_vc_number(client, session):
    """
    Verify that creating a customer with a duplicate vc_number returns 409.
    """
    # --- setup lookup data ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    create_status(session, StatusEnum.ACTIVE)
    create_status(session, StatusEnum.INACTIVE)

    ftth64 = FTTH64(
        name="FTTH-TEST"
    )
    session.add(ftth64)

    session.commit()

    #  --- first customer --- 
    payload = {
        "name": "Test Customer 1",
        "phone": "9999999998",
        "vc_number": "VC123456",
        "village_id": village.id,
        "customer_type_id": customer_type.id,
        "ftth64_id": ftth64.id,
        "package_id": package.id
    }

    response1 = client.post("/customer/", json=payload)
    data = response1.json()

    assert response1.status_code == 200
    assert data["vc_number"] == payload["vc_number"]

     # --- second customer with same vc_number ---
    payload = {
        "name": "Test Customer 2",
        "phone": "9999999992",
        "vc_number": "VC123456",
        "village_id": village.id,
        "customer_type_id": customer_type.id,
        "ftth64_id": ftth64.id,
        "package_id": package.id
    }

    # API call
    response2 = client.post("/customer/", json=payload)

    # assertions
    assert response2.status_code == 409

    # --- DB verification: second customer not persisted ---
    second_customer = session.exec(
        select(Customer).where(Customer.phone == "9999999992")
    ).first()
    assert second_customer is None

    # --- DB verification: duplicate device not created ---
    devices = session.exec(
        select(DeviceInfo).where(DeviceInfo.vc_number == "VC123456")
    ).all()
    assert len(devices) == 1


def test_get_customer_success(client, session):
    """
    Verify that a customer can be fetched by public_id.
    """
    # --- setup ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    inactive = create_status(session, StatusEnum.INACTIVE)

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
        status_id=inactive.id
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
    assert data["ftth64"] is not None
    assert data["ftth64"]["id"] == ftth64.id


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
    inactive = create_status(session, StatusEnum.INACTIVE)
    
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
            status_id=inactive.id
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
    inactive = create_status(session, StatusEnum.INACTIVE)

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
        status_id=inactive.id
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
    session.expire(customer)

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
    create_status(session, StatusEnum.ACTIVE)
    create_status(session, StatusEnum.INACTIVE)

    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.commit()

    payload = {
        "customers": [
            {
                "name": "User1",
                "phone": "8000000001",
                "vc_number": "VCB1",
                "village_id": village.id,
                "customer_type_id": customer_type.id,
                "ftth64_id": ftth64.id,
                "package_id": package.id
            },
            {
                "name": "User2",
                "phone": "7000000002",
                "vc_number": "VCB2",
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


def test_create_customers_bulk_duplicate_phone(client, session):
    """
    Verify duplicate phone causes partial failure in bulk onboarding.
    """
    # --- setup ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    create_status(session, StatusEnum.ACTIVE)
    create_status(session, StatusEnum.INACTIVE)


    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.commit()

    # --- payload ---
    payload = {
        "customers": [
            {
                "name": "User 1",
                "phone": "9000000010",
                "vc_number": "VCX1",
                "village_id": village.id,
                "customer_type_id": customer_type.id,
                "ftth64_id": ftth64.id,
                "package_id": package.id
            },
            {
                # ❌ duplicate phone
                "name": "User 2",
                "phone": "9000000010",
                "vc_number": "VCX2",
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


def test_onboard_default_status_inactive(client, session):
    """
    Verify that a newly onboarded customer's device is assigned inactive status by default,
    regardless of any status provided in the payload.
    """
    # --- setup ---
    village = create_village(session)
    package = create_package(session)
    active = create_status(session, StatusEnum.ACTIVE)
    inactive = create_status(session, StatusEnum.INACTIVE)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.commit()

    # get inactive status
    _, inactive_status_id = get_active_inactive_status_ids(session)

    payload = {
        "name": "Test User",
        "phone": "9000000100",
        "vc_number": "VC100",
        "village_id": village.id,
        "customer_type_id": customer_type.id,
        "ftth64_id": ftth64.id,
        "package_id": package.id
    }

    # --- API call ---
    response = client.post("/customer/", json=payload)
    assert response.status_code == 200

    # --- DB verification ---
    device = session.exec(
        select(DeviceInfo).where(DeviceInfo.vc_number == "VC100")
    ).first()

    assert device is not None
    assert device.status_id == inactive_status_id


def test_agent_cannot_see_other_agents_customers(raw_client, session):
    """
    Verify that an agent cannot see customers belonging to another agent's village.
    """
    agent1 = create_agent(session)
    agent2 = create_agent(session)

    v1 = create_village(session)

    v1.agent_id = agent1.id
    session.add(v1)
    session.commit()

    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    create_status(session, StatusEnum.ACTIVE)
    inactive = create_status(session, StatusEnum.INACTIVE)

    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.flush()

    # customer belongs to agent1 village
    customer = create_customer(
        session,
        village_id=v1.id,
        customer_type_id=customer_type.id,
        ftth64_id=ftth64.id,
        package_id=package.id,
        phone=str(9000000000 + uuid.uuid4().int % 100000),
        name="User 5"
    )

    device = DeviceInfo(
        public_id=str(uuid.uuid4()),
        customer_id=customer.id,
        vc_number="VC-RBAC",
        status_id=inactive.id
    )

    session.add(device)
    session.commit()

    # --- agent2 token ---
    token = create_access_token({"sub": str(agent2.public_id)})
    headers = {"Authorization": f"Bearer {token}"}

    # --- API call ---
    response = raw_client.get("/customer/", headers=headers)
    data = response.json()

    # --- assertion ---
    assert response.status_code == 200
    assert data["total"] == 0


def test_unauthenticated_user(raw_client):
    """
    Verify that accessing a protected endpoint without an authorization token returns 401.
    """
    # --- API call ---
    response = raw_client.get("/customer/no_id")

    # --- assertion ---
    assert response.status_code == 401



