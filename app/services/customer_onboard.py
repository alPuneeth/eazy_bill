from app.schemas.customers.customer_onboard import CustomerOnboardCreate
from sqlmodel import Session
# from sqlalchemy.exc import IntegrityError


from app.models.core_models.customer import Customer
from app.models.core_models.user import User
from app.models.devices.device_info import DeviceInfo
from app.models.lookup.village import Village
from app.models.lookup.customer_type import CustomerType
from app.models.lookup.package import Package
from app.models.lookup.ftth64 import FTTH64
from app.models.lookup.status import Status
from app.models.lookup.tv_type import TVType


def onboard_single_customer(
    payload: CustomerOnboardCreate,
    session: Session,
    current_user: User
) -> Customer:
    """
    Creates ONE customer and ONE device.
    Does NOT commit.
    Raises ValueError / PermissionError.
    """

    village = session.get(Village, payload.village_id)
    if not village:
        raise ValueError("Invalid village")

    # if current_user.role == "agent" and village.agent_restricted:
    #     raise PermissionError("Restricted village")

    if not session.get(CustomerType, payload.customer_type_id):
        raise ValueError("Invalid customer type")

    if not session.get(FTTH64, payload.ftth64_id):
        raise ValueError("Invalid FTTH64")

    if not session.get(Package, payload.package_id):
        raise ValueError("Invalid package")

    if not session.get(Status, payload.status_id):
        raise ValueError("Invalid status")

    if payload.tvtype_id is not None:
        if not session.get(TVType, payload.tvtype_id):
            raise ValueError("Invalid TV type")

    # 1. Customer
    customer = Customer(
        name=payload.name,
        phone=payload.phone,
        alternate_number=payload.alternate_number,
        aadhaar_number=payload.aadhaar_number,
        upi_id=payload.upi_id,
        village_id=payload.village_id,
        customer_type_id=payload.customer_type_id,
        ftth8_code=payload.ftth8_code,
        ftth64_id=payload.ftth64_id,
        package_id=payload.package_id,
        description=payload.description,
    )

    session.add(customer)
    session.flush()  # critical to get customer.id

    # 2. DeviceInfo (exactly ONE device per onboard)
    device = DeviceInfo(
        customer_id=customer.id,
        account_number=payload.account_number,
        stb_id=payload.stb_id,
        vc_number=payload.vc_number,
        previous_vc_number=payload.previous_vc_number,
        tv_name=payload.tv_name,
        tvtype_id=payload.tvtype_id,
        status_id=payload.status_id,
    )

    session.add(device)

    return customer
