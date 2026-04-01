from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from datetime import date

from app.dependencies.rbac import get_current_user
from app.services.status_ids import get_active_inactive_status_ids
from app.services.device_status import sync_device_status_from_bills
from app.services.bill_service import generate_bill_code
from app.models.lookup.status import StatusEnum, Status

from app.models.lookup.village import Village
from app.services.customer.enforce_customer_vis import enforce_customer_visibility
from app.models.core_models.user import User
from app.db.session import get_session
from app.models.core_models.customer import Customer
from app.models.lookup.package import Package
from app.schemas.common import IdValueRead
from app.models.bill.bill import Bill
from app.schemas.bill import (
    BillCreate,
    BillRead,
    BillUpdate
)

router = APIRouter(
    prefix="/bill",
    tags=["Bill"]
    )


# all bills
@router.get("/", response_model=list[BillRead])
def list_bills(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    
    stmt = (
        select(
            Bill.public_id,
            Bill.bill_code,
            Bill.bill_date,
            Bill.start_date,
            Bill.end_date,
            Bill.monthly_count,
            Bill.bill_amount,
            Customer.public_id.label("customer_public_id"),
            Package.id.label("package_id"),
            Package.name.label("package_value"),
            User.id.label("created_by_id"),
            User.name.label("created_by_value"),
            Bill.created_at,
            Bill.updated_at,
        )
        .join(Customer, Customer.id == Bill.customer_id)
        .join(Village, Village.id == Customer.village_id)
        .join(Package, Package.id == Bill.package_id)
        .join(User, User.id == Bill.created_by_id)
        .order_by(desc(Bill.bill_date))
    )

    # # 🔐 enforce visibility at DB level
    if current_user.role != "agent":
        pass
    
    else:
        stmt = stmt.where(Village.agent_id == current_user.id)


    rows = session.exec(stmt).mappings().all()

    return [
        BillRead(
            public_id=r["public_id"],
            bill_code=r["bill_code"],
            bill_date=r["bill_date"],
            start_date=r["start_date"],
            end_date=r["end_date"],
            monthly_count=r["monthly_count"],
            bill_amount=r["bill_amount"],
            customer_public_id=r["customer_public_id"],
            package_id=IdValueRead(
                id=r["package_id"],
                value=r["package_value"]
            ),
            created_by_id=IdValueRead(
                id=r["created_by_id"],
                value=r["created_by_value"]
            ),
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
        for r in rows
    ]



@router.get("/generate_bill_code/{village_code}", response_model=str)
def get_bill_code(
    village_code: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
                  ):
    village = session.exec(
        select(Village).where(Village.village_code == village_code)
    ).first()

    if not village:
        raise HTTPException(
            status_code=404,
            detail="Village not found"
        )

    return generate_bill_code(village.id, session, current_user)


# bill
@router.get("/{bill_public_id}", response_model=BillRead)
def get_bill(
    bill_public_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    bill = session.exec(
        select(Bill).where(Bill.public_id == bill_public_id)
    ).one_or_none()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    customer = session.get(Customer, bill.customer_id)
    if not customer:
        raise HTTPException(
            status_code=500,
            detail="Customer not found for bill"
        )

    enforce_customer_visibility(
                                customer=customer,
                                current_user=current_user,
                                session=session,
                                )
    
    package = session.get(Package, bill.package_id)
    if not package:
        raise HTTPException(
            status_code=500,
            detail="Package not found for bill"
        )

    creator = session.get(User, bill.created_by_id)
    if not creator:
        raise HTTPException(500, "Creator not found for bill")

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
                    created_by_id=IdValueRead(
                        id=current_user.id,
                        value=current_user.name
                    ),
                    created_at=bill.created_at,
                    updated_at=bill.updated_at,
                )


@router.post("/", response_model=BillRead)
def create_bill(
    payload: BillCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 1. Resolve customer
    customer = session.exec(
        select(Customer).where(
            Customer.public_id == payload.customer_public_id
        )
    ).one_or_none()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    enforce_customer_visibility(
        customer=customer,
        current_user=current_user,
        session=session,
    )

    # 2. Validate package
    package = session.get(Package, payload.package_id)
    if not package:
        raise HTTPException(
            status_code=400,
            detail="Invalid package"
        )

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

    session.add(bill)

    try:
        # 4. Persist bill
        session.commit()
        session.refresh(bill)

        # 5. Resolve ACTIVE / INACTIVE status ids
        active_status_id, inactive_status_id = (
            get_active_inactive_status_ids(session)
        )

        # 6. Sync device status based on bill period
        sync_device_status_from_bills(
            customer_id=customer.id,
            session=session,
            active_status_id=active_status_id,
            inactive_status_id=inactive_status_id,
        )

        # 7. Persist device updates
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate bill_code or invalid bill"
        )

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
        created_by_id=IdValueRead(
            id=current_user.id,
            value=current_user.name
        ),
        created_at=bill.created_at,
        updated_at=bill.updated_at,
    )


@router.patch("/{bill_public_id}", response_model=BillRead)
def update_bill(
    bill_public_id: str,
    payload: BillUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    bill = session.exec(
        select(Bill).where(Bill.public_id == bill_public_id)
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    customer = session.get(Customer, bill.customer_id)
    if not customer:
        raise HTTPException(500, "Customer not found for bill")

    enforce_customer_visibility(
        customer=customer,
        current_user=current_user,
        session=session,
    )

    if bill.created_at.date() != date.today():
        raise HTTPException(
            status_code=400,
            detail="Bills cannot be modified after the day of creation"
        )

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )
    for key, value in update_data.items():
        setattr(bill, key, value)

    try:
        session.commit()
        session.refresh(bill)

        # Resolve ACTIVE / INACTIVE ids
        active_status_id, inactive_status_id = (
            get_active_inactive_status_ids(session)
        )

        # Sync device status
        sync_device_status_from_bills(
            customer_id=bill.customer_id,
            session=session,
            active_status_id=active_status_id,
            inactive_status_id=inactive_status_id,
        )

        # Persist device updates
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=409,
            detail="Duplicate bill_code or invalid foreign key"
            )

    package = session.get(Package, bill.package_id)
    if not package:
        raise HTTPException(500, "Package not found for bill")

    customer = session.get(Customer, bill.customer_id)
    if not customer:
        raise HTTPException(500, "Customer not found for bill")

    creator = session.get(User, bill.created_by_id)
    if not creator:
        raise HTTPException(500, "Creator not found for bill")

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
                    created_by_id=IdValueRead(
                        id=creator.id,
                        value=creator.name
                    ),
                    created_at=bill.created_at,
                    updated_at=bill.updated_at,
                )


# bill by customer public id
@router.get(
    "/customer/{customer_public_id}",
    response_model=list[BillRead]
)
def get_bills_by_customer(
    customer_public_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Resolve customer
    customer = session.exec(
        select(Customer).where(Customer.public_id == customer_public_id)
    ).one_or_none()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

     # Enforce visibility
    enforce_customer_visibility(
                                customer=customer,
                                current_user=current_user,
                                session=session
                                )


    # 2. Fetch bills for this customer
    stmt = (
        select(
            Bill.public_id,
            Bill.bill_code,
            Bill.bill_date,
            Bill.start_date,
            Bill.end_date,
            Bill.monthly_count,
            Bill.bill_amount,

            Customer.public_id.label("customer_public_id"),

            Package.id.label("package_id"),
            Package.name.label("package_value"),

            User.id.label("created_by_id"),
            User.name.label("created_by_value"),

            Bill.created_at,
            Bill.updated_at,
        )
        .join(Customer, Customer.id == Bill.customer_id)
        .join(Package, Package.id == Bill.package_id)
        .join(User, User.id == Bill.created_by_id)
        .where(Customer.id == customer.id)
        .order_by(desc(Bill.bill_date))
    )

    rows = session.execute(stmt).mappings().all()

    return [
        BillRead(
            public_id=r["public_id"],
            bill_code=r["bill_code"],
            bill_date=r["bill_date"],
            start_date=r["start_date"],
            end_date=r["end_date"],
            monthly_count=r["monthly_count"],
            bill_amount=r["bill_amount"],
            customer_public_id=r["customer_public_id"],
            package_id=IdValueRead(
                id=r["package_id"],
                value=r["package_value"]
            ),
            created_by_id=IdValueRead(
                id=r["created_by_id"],
                value=r["created_by_value"]
            ),
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
        for r in rows
    ]