from datetime import datetime, timedelta
import uuid

from app.models.bill.bill import Bill
from app.models.devices.device_info import DeviceInfo
from app.models.lookup.customer_type import CustomerTypeEnum
from app.models.lookup.ftth64 import FTTH64

from app.models.lookup.status import StatusEnum
from tests.factories.customer import create_customer, create_customer_type
from tests.factories.status import create_status
from tests.factories.user import create_admin
from tests.factories.package import create_package
from tests.factories.village import create_village


def create_bill(session,
                customer_id=None,
                created_by_id=None,
                bill_code=None,
                bill_date=None,
                start_date=None,
                end_date=None,
                monthly_count=None,
                bill_amount=None,
                public_id=None,
                package_id=None
                ):
    
    bill_code = bill_code or "VC001KVR26-001"
    bill_date = bill_date or datetime.today()
    start_date = start_date or datetime.today()
    end_date = end_date or datetime.today() + timedelta(days=30)
    monthly_count = monthly_count or 1
    bill_amount = bill_amount or 500
    public_id = public_id or str(uuid.uuid4())
    package_id = package_id or create_package(session).id

    create_status(session, StatusEnum.ACTIVE)
    inactive = create_status(session, StatusEnum.INACTIVE)


    if customer_id is None:
        village = create_village(session)
        customer_type = create_customer_type(session, CustomerTypeEnum.REGULAR)
        ftth64 = FTTH64(name="FTTH-TEST")
        session.add(ftth64)
        session.flush()

        customer_id = create_customer(
            session,
            village_id=village.id,
            customer_type_id=customer_type.id,
            ftth64_id=ftth64.id,
            package_id=package_id
        ).id
    

        device_info = DeviceInfo(
            public_id=str(uuid.uuid4()),
            customer_id=customer_id,
            vc_number=f"VC-{str(uuid.uuid4())[:5]}",
            status_id=inactive.id
        )
        session.add(device_info)
        session.flush()
    
    if created_by_id is None:
        created_by_id = create_admin(session).id

    bill = Bill(
        customer_id=customer_id,
        created_by_id=created_by_id,
        bill_code=bill_code,
        bill_date=bill_date,
        start_date=start_date,
        end_date=end_date,
        monthly_count=monthly_count,
        bill_amount=bill_amount,
        public_id=public_id,
        package_id=package_id
    )

    session.add(bill)
    session.flush()
    return bill
