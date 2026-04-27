from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from datetime import date

from app.models.bill.bill import Bill
from app.models.core_models.customer import Customer
from app.models.lookup.package import Package
from app.models.core_models.user import User

from app.schemas.bill import BillRead, BillUpdate
from app.schemas.common import IdValueRead, CreatorSummary

from app.services.bill.bill_exceptions import (
    BillConflictError,
    CustomerNotFoundError,
    InvalidPackageError,
    BillNotFoundError,
    BillUpdateNotAllowedError,
    EmptyUpdateError,
    OverlappinBillingPeriod
)
from app.services.customer.enforce_customer_vis import enforce_customer_visibility
from app.services.device_status import sync_device_status_from_bills
from app.services.status_ids import get_active_inactive_status_ids

def update_bll(
    bill_public_id: str,
    payload: BillUpdate,
    session: Session,
    current_user: User
)-> BillRead:
    """
    Service layer:
    - No HTTPException
    - Handles validation, RBAC, transaction
    """

    # 1. Fetch bill
    bill = session.exec(
        select(Bill).where(Bill.public_id == bill_public_id)
    ).first()

    if not bill:
        raise BillNotFoundError()

    # 2. Resolve customer (for RBAC)
    customer = session.get(Customer, bill.customer_id)
    if not customer:
        raise CustomerNotFoundError()

    enforce_customer_visibility(
        customer=customer,
        current_user=current_user,
        session=session,
    )

    # 3. Business rule: same-day update only

    if bill.created_at.date() != date.today():
        raise BillUpdateNotAllowedError()

    # 4. Extract update payload
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise EmptyUpdateError()

    # 5. validate package if changed
    if "package_id" in update_data:
        package = session.get(Package, update_data["package_id"])
        if not package:
            raise InvalidPackageError()
    
    try:
        with session.begin(): 
            # lock customer (same as create)
            session.exec(
                select(Customer)
                .where(Customer.id == customer.id)
                .with_for_update()
            ).one()

            new_start = update_data.get("start_date", bill.start_date)
            new_end = update_data.get("end_date", bill.end_date)

            # overlap check excluding current bill
            existing_overlap = session.exec(
                select(Bill).where(
                    Bill.customer_id == customer.id,
                    Bill.id != bill.id,   # 🔥 critical
                    Bill.start_date <= new_end,
                    Bill.end_date >= new_start
                )
            ).first()

            if existing_overlap:
                raise OverlappinBillingPeriod()
            
            # mutation
            for key, value in update_data.items():
                setattr(bill, key, value)

            session.add(bill)

            # 7. flush() generates bill.id without committing - prepare changes
            session.flush()

            # 8. Resolve status ids
            active_status_id, inactive_status_id = (
                get_active_inactive_status_ids(session)
            )

            # 9. Sync device status
            sync_device_status_from_bills(
                customer_id=bill.customer_id,
                session=session,
                active_status_id=active_status_id,
                inactive_status_id=inactive_status_id,
            )

    except IntegrityError:
        raise BillConflictError()
    
    package = session.get(Package, bill.package_id)

    creator = session.get(User, bill.created_by_id)
    if not creator:
        raise Exception("Creator missing") # rare system-level issue

    # 12. Map response
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
                        id=package.id,
                        value=package.name
                    ),
                    created_by_id=CreatorSummary(
                        id=creator.id,
                        public_id=creator.public_id,
                        name=creator.name
                    ),
                    created_at=bill.created_at,
                    updated_at=bill.updated_at,
                )
