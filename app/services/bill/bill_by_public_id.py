from sqlmodel import Session, select

from app.models.core_models.user import User
from app.models.core_models.customer import Customer
from app.models.lookup.package import Package
from app.models.bill.bill import Bill

from app.schemas.common import IdValueRead, CreatorSummary                                       
from app.schemas.bill import BillRead

from app.services.customer.enforce_customer_vis import enforce_customer_visibility
from app.services.bill.bill_exceptions import BillNotFoundError


def get_bill_by_public_id(bill_public_id: str, current_user:User, session:Session)-> BillRead:
    """
    Service layer:
    - Handles DB querying
    - Handles RBAC
    - Returns DTO(Data Transfer Object)
    - Raises domain exceptions (NOT HTTP)
    """
    stmt = select(
        Bill,
        Customer.public_id.label("customer_public_id"),
        Package.id.label("package_id"),
        Package.name.label("package_name"),
        User.id.label("creator_id"),
        User.public_id.label("creator_public_id"),
        User.name.label("creator_name"),
    ).join(Customer, Customer.id == Bill.customer_id).join(Package, Package.id == Bill.package_id).join(User, User.id == Bill.created_by_id).where(Bill.public_id == bill_public_id)

    row = session.exec(stmt).first()

    if not row:
        raise BillNotFoundError()
    
    bill = row[0]

    # RBAC
    enforce_customer_visibility(
        customer=bill.customer,
        current_user=current_user,
        session=session
    )

    return BillRead(
        public_id=bill.public_id,
        bill_code=bill.bill_code,
        bill_date=bill.bill_date,
        start_date=bill.start_date,
        end_date=bill.end_date,
        monthly_count=bill.monthly_count,
        bill_amount=bill.bill_amount,
        customer_public_id=row.customer_public_id,
        package_id=IdValueRead(
            id=row.package_id,
            value=row.package_name
        ),
        created_by_id=CreatorSummary(
            public_id=row.creator_public_id,
            name=row.creator_name
        ),
        created_at=bill.created_at,
        updated_at=bill.updated_at,
    )



