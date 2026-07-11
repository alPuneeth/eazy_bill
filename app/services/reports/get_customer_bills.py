from sqlmodel import select, Session
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload

from app.models.core_models.customer import Customer
from app.schemas.bill import BillRead
from app.models.core_models.user import User
from app.models.core_models.user import UserRole
from app.models.lookup.village import Village
from app.models.bill.bill import Bill
from app.schemas.common import IdValueRead, CreatorSummary


def get_customer_bills_all_time(
    *,
    session: Session,
    customer_public_id: str,
    current_user: User
) -> list[BillRead]:

    customer = session.exec(
        select(Customer)
        .where(Customer.public_id == customer_public_id)
    ).one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    if current_user.role == UserRole.AGENT:
        village = session.get(Village, customer.village_id)

        if not village or village.agent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this customer"
            )
        
    stmt = (
        select(Bill)
        .where(Bill.customer_id == customer.id)
        .options(
                joinedload(Bill.package),
                joinedload(Bill.created_by)
                    )
        .order_by(Bill.bill_date.desc())
    )

    bills = session.exec(stmt).all()
    return [BillRead(
        public_id=bill.public_id,
        bill_code=bill.bill_code,
        bill_date=bill.bill_date,
        start_date=bill.start_date,
        end_date=bill.end_date,
        monthly_count=bill.monthly_count,
        bill_amount=bill.bill_amount,

        customer_public_id=customer.public_id,

        package_id=IdValueRead(
            id=bill.package.id,
            value=bill.package.name
        ),

        created_by_id=CreatorSummary(
            id=bill.created_by_id,
            public_id=bill.created_by.public_id,
            name=bill.created_by.name
        ),

        created_at=bill.created_at,
        updated_at=bill.updated_at
    )
    for bill in bills
]