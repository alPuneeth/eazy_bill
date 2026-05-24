from datetime import date, datetime, timedelta
import uuid

from sqlmodel import select

from app.models.core_models.customer import Customer
from app.models.devices.device_info import DeviceInfo
from app.models.lookup.customer_type import CustomerTypeEnum
from app.models.lookup.ftth64 import FTTH64
from app.models.lookup.status import StatusEnum
from tests.factories.bill_creation import create_bill
from tests.factories.customer import create_customer, create_customer_type
from tests.factories.package import create_package
from tests.factories.status import create_status
from tests.factories.village import create_village


def test_create_bill_success(client, session):
    """
    Verify that a bill is created successfully and device status is synced to active.
    """
    # --- setup ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    active = create_status(session, StatusEnum.ACTIVE)
    inactive = create_status(session, StatusEnum.INACTIVE)

    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.flush()

    customer = create_customer(
        session,
        village_id=village.id,
        customer_type_id=customer_type.id,
        ftth64_id=ftth64.id,
        package_id=package.id
    )

    device = DeviceInfo(
        public_id=str(uuid.uuid4()),
        customer_id=customer.id,
        vc_number="VC-BILL-001",
        status_id=inactive.id
    )
    session.add(device)
    session.commit()

    # --- payload ---
    today = datetime.today()
    payload = {
        "bill_code": "VC001KVR26-001",
        "bill_date": today.isoformat(),
        "start_date": today.isoformat(),
        "end_date": (today + timedelta(days=30)).isoformat(),
        "monthly_count": 1,
        "bill_amount": 500,
        "customer_public_id": customer.public_id,
        "package_id": package.id
    }

    # --- API call ---
    response = client.post("/bill/", json=payload)
    data = response.json()

    # --- assertions ---
    assert response.status_code == 200
    assert data["bill_code"] == payload["bill_code"]
    assert data["customer_public_id"] == customer.public_id

    # --- DB verification: device status synced to active ---
    session.expire(device)
    updated_device = session.exec(
        select(DeviceInfo).where(DeviceInfo.id == device.id)
    ).first()

    assert updated_device.status_id == active.id
    assert updated_device.status.name == StatusEnum.ACTIVE


def test_create_bill_overlapping_period(client, session):
    """
    Verify that creating a bill with an overlapping billing period returns 409.
    """
    # --- setup ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    create_status(session, StatusEnum.ACTIVE)
    inactive = create_status(session, StatusEnum.INACTIVE)

    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.flush()

    customer = create_customer(
        session,
        village_id=village.id,
        customer_type_id=customer_type.id,
        ftth64_id=ftth64.id,
        package_id=package.id
    )

    device = DeviceInfo(
        public_id=str(uuid.uuid4()),
        customer_id=customer.id,
        vc_number="VC-OVERLAP-001",
        status_id=inactive.id
    )
    session.add(device)
    session.commit()

    today = datetime.today()

    # --- first bill ---
    first_payload = {
        "bill_code": "VC001KVR26-001",
        "bill_date": today.isoformat(),
        "start_date": today.isoformat(),
        "end_date": (today + timedelta(days=30)).isoformat(),
        "monthly_count": 1,
        "bill_amount": 500,
        "customer_public_id": customer.public_id,
        "package_id": package.id
    }
    first_response = client.post("/bill/", json=first_payload)
    assert first_response.status_code == 200

    # --- overlapping bill ---
    overlap_payload = {
        "bill_code": "VC001KVR26-002",
        "bill_date": (today + timedelta(days=15)).isoformat(),
        "start_date": (today + timedelta(days=15)).isoformat(),
        "end_date": (today + timedelta(days=45)).isoformat(),
        "monthly_count": 1,
        "bill_amount": 500,
        "customer_public_id": customer.public_id,
        "package_id": package.id
    }
    response = client.post("/bill/", json=overlap_payload)

    assert response.status_code == 409


def test_create_bill_duplicate_code(client, session, admin_user):
    """
    Verify that creating a bill with a duplicate bill_code returns 409.
    """
    bill = create_bill(session, created_by_id=admin_user.id)

    customer = session.get(Customer, bill.customer_id)

    now = datetime.now()

    payload = {
        "bill_code": bill.bill_code,  # duplicate
        "bill_date": now.isoformat(),
        "start_date": now.isoformat(),
        "end_date": bill.end_date.isoformat(),
        "monthly_count": 1,
        "bill_amount": 500,
        "customer_public_id": customer.public_id,
        "package_id": bill.package_id 
    }

    response = client.post("/bill/", json=payload)
    assert response.status_code in (400, 409)


def test_create_bill_invalid_date_range(client, session, admin_user):
    """
    Verify that creating a bill where end_date is before start_date returns 422.
    """
    bill = create_bill(session, created_by_id=admin_user.id)
    customer = session.get(Customer, bill.customer_id)

    now = datetime.now()

    payload = {
        "bill_code": "INVALID-001",
        "bill_date": now.isoformat(),
        "start_date": now.isoformat(),
        "end_date": (now - timedelta(days=1)).isoformat(),
        "monthly_count": 1,
        "bill_amount": 500,
        "customer_public_id": customer.public_id,
        "package_id": bill.package_id 
    }

    response = client.post("/bill/", json=payload)
    assert response.status_code == 422


def test_get_bill_success(client, session, admin_user):
    """
    Verify that a bill can be fetched by public_id.
    """
    bill = create_bill(session, created_by_id=admin_user.id)

    response = client.get(f"/bill/{bill.public_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["public_id"] == bill.public_id
    assert data["bill_code"] == bill.bill_code


def test_get_bill_failure(client):
    """
    Verify that fetching a non-existent bill returns 404.
    """
    public_id = str(uuid.uuid4())
    response = client.get(f"/bill/{public_id}")
    assert response.status_code == 404


def test_update_bill_success(client, session, admin_user):
    """
    Verify that updating a bill on the same day of its creation is allowed.
    """
    bill = create_bill(session, created_by_id=admin_user.id)

    assert bill.bill_amount == 500.0

    payload = {
        "bill_amount": 600
    }

    response = client.patch(f"/bill/{bill.public_id}", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["bill_amount"] == 600.0


def test_update_bill_not_on_bill_date(client, session, admin_user):
    """
    Verify that modifying a bill on a date other than its bill_date returns 400.
    """
    bill = create_bill(session, created_by_id=admin_user.id)

    assert bill.bill_date.date() == date.today()

    bill.bill_date =  datetime.combine(
        date.today() - timedelta(days=1),
        datetime.min.time()
        )
    session.flush()
    
    payload = {
        "start_date": datetime.combine(
            date.today() + timedelta(days=10),
            datetime.min.time()).isoformat()
    }

    response = client.patch(f"/bill/{bill.public_id}", json=payload)

    assert response.status_code == 400


def test_bills_by_customer_public_id(client, session, admin_user):
    """
    Verify that bills for a valid customer can be fetched and returns the correct bill data.
    """
    bill = create_bill(session, created_by_id=admin_user.id)

    customer = session.exec(
        select(Customer).where(bill.customer_id == Customer.id)
    ).first()

    response = client.get(f"/bill/customer/{customer.public_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["bill_amount"] == bill.bill_amount
    assert data["items"][0]["public_id"] == bill.public_id

    
def test_update_bill_overlap(client, session, admin_user):
    """
    Verify that updating a bill to overlap with an existing bill period returns 409.
    """
    today = datetime.today()

    bill1 = create_bill(
        session,
        created_by_id=admin_user.id,
        bill_code="VC001KVR26-001",
        bill_date=today,
        start_date=today,
        end_date=today + timedelta(days=30)
    )

    bill2 = create_bill(
        session,
        created_by_id=admin_user.id,
        customer_id=bill1.customer_id,
        bill_code="VC001KVR26-002",
        bill_date=today,
        start_date=today + timedelta(days=31),
        end_date=today + timedelta(days=60)
    )

    payload = {
        "start_date": bill1.start_date.isoformat(),
        "end_date": bill1.end_date.isoformat()
    }

    response = client.patch(f"/bill/{bill2.public_id}", json=payload)
    assert response.status_code == 409


def test_create_bill_unauthorized(raw_client):
    """
    Verify that creating a bill without authentication returns 401.
    """
    response = raw_client.post("/bill/", json={})
    assert response.status_code == 401


def test_create_bill_for_archived_customer_returns_error(client, session):
    """
    Archived customers cannot be billed.
    Bill creation must return 409 when the customer's device is archived.
    """

    # --- setup ---
    village = create_village(session)
    package = create_package(session)
    customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
    archived = create_status(session, StatusEnum.ARCHIVED)


    ftth64 = FTTH64(name="FTTH-TEST")
    session.add(ftth64)
    session.flush()

    customer = create_customer(
        session,
        village_id=village.id,
        customer_type_id=customer_type.id,
        ftth64_id=ftth64.id,
        package_id=package.id
    )

    device = DeviceInfo(
        public_id=str(uuid.uuid4()),
        customer_id=customer.id,
        vc_number="VC-BILL-001",
        status_id=archived.id
    )

    session.add(device)
    session.commit()

    today = datetime.today()

    payload = {
        "bill_code": "VC001KVR26-0032",
        "bill_date": today.isoformat(),
        "start_date": today.isoformat(),
        "end_date": (today + timedelta(days=30)).isoformat(),
        "monthly_count": 1,
        "bill_amount": 1500,
        "customer_public_id": customer.public_id,
        "package_id": package.id
    }

    # --- API call ---
    response = client.post("/bill/", json=payload)
    data = response.json()

    assert response.status_code == 409
    assert "archived" in data["detail"].lower()






