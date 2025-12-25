from sqlmodel import Session
from sqlalchemy import select

from app.schemas.customers.customer_onboard import (
    CustomerOnboardRead
    )
from app.schemas.common import IdValueRead

from app.models.core_models.customer import Customer
from app.models.devices.device_info import DeviceInfo
from app.models.lookup.village import Village
from app.models.lookup.customer_type import CustomerType
from app.models.lookup.ftth64 import FTTH64
from app.models.lookup.tv_type import TVType
from app.models.lookup.status import Status
from app.models.lookup.package import Package


def build_customer_onboard_read_from_customer(
    customer: Customer,
    session: Session,
) -> CustomerOnboardRead:

    stmt = (
        select(
            Village,
            CustomerType,
            FTTH64,
            Package,
            DeviceInfo,
            TVType,
            Status,
        )
        .select_from(Customer)
        .join(Village, Village.id == Customer.village_id)
        .join(CustomerType, CustomerType.id == Customer.customer_type_id)
        .join(FTTH64, FTTH64.id == Customer.ftth64_id)
        .outerjoin(Package, Package.id == Customer.package_id)
        .outerjoin(DeviceInfo, DeviceInfo.customer_id == Customer.id)
        .outerjoin(TVType, TVType.id == DeviceInfo.tvtype_id)
        .outerjoin(Status, Status.id == DeviceInfo.status_id)
        .where(Customer.id == customer.id)
        )

    (
        village,
        customer_type,
        ftth64,
        package_,
        device,
        tvtype,
        status,
    ) = session.execute(stmt).one()

    return CustomerOnboardRead(
        public_id=customer.public_id,
        name=customer.name,
        phone=customer.phone,
        alternate_number=customer.alternate_number,
        aadhaar_number=customer.aadhaar_number,
        upi_id=customer.upi_id,

        village=IdValueRead(id=village.id, value=village.name),
        customer_type=IdValueRead(id=customer_type.id, value=customer_type.name),
        ftth64=IdValueRead(id=ftth64.id, value=ftth64.name),

        description=customer.description,

        account_number=device.account_number if device else None,
        stb_id=device.stb_id if device else None,
        vc_number=device.vc_number if device else None,
        previous_vc_number=device.previous_vc_number if device else None,
        tv_name=device.tv_name if device else None,

        tvtype=IdValueRead(id=tvtype.id, value=tvtype.name) if tvtype else None,
        status=IdValueRead(id=status.id, value=status.name) if status else None,

        package=(
            IdValueRead(id=package_.id, value=package_.name)
            if package_ else None
        ),
        monthly_rate=package_.price if package_ else None,

        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )
