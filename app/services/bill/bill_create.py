from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.models.bill.bill import Bill
from app.models.core_models.customer import Customer
from app.models.lookup.package import Package
from app.models.core_models.user import User

from app.schemas.bill import BillRead, BillCreate
from app.schemas.common import IdValueRead, CreatorSummary

from app.services.bill.bill_exceptions import (
    BillConflictError,
    OverlappingBillingPeriod,
    CustomerNotFoundError,
    InvalidPackageError
)
from app.services.customer.enforce_customer_vis import enforce_customer_visibility
from app.services.device_status import sync_device_status_from_bills
from app.services.status_ids import get_active_inactive_status_ids


def create_bll(
    payload: BillCreate,
    session: Session,
    current_user: User
) -> BillRead:
    """
    Service layer:
    - Business logic
    - DB operations
    - Transaction handling
    """

    # 1. Resolve customer
    customer = session.exec(
        select(Customer).where(
            Customer.public_id == payload.customer_public_id
        )
    ).one_or_none()

    if not customer:
        raise CustomerNotFoundError()

    # RBAC
    enforce_customer_visibility(
        customer=customer,
        current_user=current_user,
        session=session,
    )

    # 2. Validate package
    package = session.get(Package, payload.package_id)
    if not package:
        raise InvalidPackageError()
    

    # 3. Create bill
    bill = Bill(
        bill_code=payload.bill_code,
        bill_date=payload.bill_date,
        start_date=payload.start_date,
        end_date=payload.end_date,
        monthly_count=payload.monthly_count,
        bill_amount=payload.bill_amount,
        customer_id=customer.id,
        package_id=payload.package_id,
        created_by_id=current_user.id,
    )

    try:
        with session.begin_nested():

            session.exec(
                select(Customer)
                .where(Customer.id == customer.id)
                .with_for_update()
                ).one()
            
            # Prevents overlapping billing periods to ensure consistent subscription timelines
            existing_overlap = session.exec(
            select(Bill).where(
                Bill.customer_id == customer.id,
                Bill.start_date <= payload.end_date,
                Bill.end_date >= payload.start_date
            )
            ).first()

            if existing_overlap:
                raise OverlappingBillingPeriod()
             
            session.add(bill)
            session.flush()

            # 5. Status resolution
            active_status_id, inactive_status_id = (
                get_active_inactive_status_ids(session)
            )

            # 6. Sync devices
            sync_device_status_from_bills(
                customer_id=customer.id,
                session=session,
                active_status_id=active_status_id,
                inactive_status_id=inactive_status_id,
            )

    except IntegrityError:
        raise BillConflictError()
    
    session.commit()
    session.refresh(bill)

    # 8. Map response
    return BillRead(
        public_id=bill.public_id,
        bill_code=bill.bill_code,
        bill_date=bill.bill_date,
        start_date=bill.start_date,
        end_date=bill.end_date,
        monthly_count=bill.monthly_count,
        bill_amount=bill.bill_amount,
        customer_public_id=customer.public_id,
        package_id=IdValueRead(
            id=bill.package_id,
            value=package.name
        ),
        created_by_id=CreatorSummary(
            id=current_user.id,
            public_id=current_user.public_id,
            name=current_user.name
        ),
        created_at=bill.created_at,
        updated_at=bill.updated_at,
    )



