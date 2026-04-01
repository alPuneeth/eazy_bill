from sqlmodel import Session, select
from fastapi import Depends
from datetime import datetime, time
from sqlalchemy import label, func

from app.db.session import get_session
from app.schemas.user import UserRole
from app.models.core_models.customer import Customer
from app.schemas.common import IdValueRead
from app.models.lookup.village import Village
from app.models.lookup.package import Package
from app.models.core_models.user import User
from app.models.bill.bill import Bill
from app.schemas.reports.bills_by_optional_filters import(
    BillFilterRequest, BillFilterRead, BillFilterResponse
    )
from app.dependencies.auth import get_current_user


def bill_op_filters(
        filters: BillFilterRequest,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
                      ):

    # selecting only the needed columns from the tables is called Projection.
    # It is used mainly when data from multiple tables are required. It returns rows not ORM objects and avoids n+1 problem.
    stmt = (
        select(
            # ---- Bill ----
            Bill.public_id,
            Bill.bill_code,
            Bill.bill_date,
            Bill.start_date,
            Bill.end_date,
            Bill.monthly_count,
            Bill.bill_amount,
            Bill.created_at,
            Bill.updated_at,

            # ---- Customer ----
            Customer.public_id.label("customer_public_id"),
            Customer.name.label("customer_name"),

            # ---- Package ----
            Package.id.label("package_id"),
            Package.name.label("package_name"),

            # ---- User ----
            User.id.label("created_by_id"),
            User.name.label("created_by_name"),
        )
        .join(Customer, Bill.customer_id == Customer.id)
        .join(Package, Customer.package_id == Package.id)
        .join(User, Bill.created_by_id == User.id)
    )
    
    need_village = filters.agent_ids is not None or current_user.role == UserRole.AGENT

    if need_village:
        stmt = stmt.join(Village, Customer.village_id == Village.id)
    
    # RBAC
    if current_user.role == UserRole.AGENT:
        stmt = stmt.where(Village.agent_id == current_user.id)

    from_dt = None
    to_dt = None

    if filters.from_date:
        from_dt = datetime.combine(filters.from_date, time.min)

    if filters.to_date:
        to_dt = datetime.combine(filters.to_date, time.max)


    # ---- Date filters ----
    if filters.from_date is not None:
        stmt = stmt.where(Bill.bill_date >= from_dt) 

    if filters.to_date is not None:
        stmt =stmt.where(Bill.bill_date <= to_dt)

    # ---- Other filters ----
    if filters.village_ids is not None:
        stmt = stmt.where(Customer.village_id.in_(filters.village_ids))


    if filters.ftth64_ids is not None:
        stmt = stmt.where(Customer.ftth64_id.in_(filters.ftth64_ids))


    if filters.agent_ids is not None:
        stmt = stmt.where(Village.agent_id.in_(filters.agent_ids))
    
      # ---- Execute main query ----
    rows = session.exec(stmt).all()

    # ---- Map to response ----
    data = [
        BillFilterRead(
            public_id=row.public_id,
            bill_code=row.bill_code,
            bill_date=row.bill_date,
            start_date=row.start_date,
            end_date=row.end_date,
            monthly_count=row.monthly_count,
            bill_amount=row.bill_amount,

            customer_public_id=row.customer_public_id,
            customer_name=row.customer_name,

            package=IdValueRead(
                id=row.package_id,
                value=row.package_name
            ),

            created_by=IdValueRead(
                id=row.created_by_id,
                value=row.created_by_name
            ),

            created_at=row.created_at,
            updated_at=row.updated_at,

        )
        for row in rows
    ]

    # ---- Total amount (only if date filter exists) ----
    total_amount = None

    if filters.from_date or filters.to_date:
        total_stmt = (
            select(func.sum(Bill.bill_amount))
            .join(Customer, Bill.customer_id == Customer.id)
            .join(Package, Customer.package_id == Package.id)
            .join(User, Bill.created_by_id == User.id)
        )

    if filters.agent_ids:
        total_stmt = total_stmt.join(Village, Customer.village_id == Village.id)

    if filters.from_date:
        total_stmt = total_stmt.where(Bill.bill_date >= from_dt)

    if filters.to_date:
        total_stmt = total_stmt.where(Bill.bill_date <= to_dt)

    if filters.village_ids:
        total_stmt = total_stmt.where(Customer.village_id.in_(filters.village_ids))

    if filters.ftth64_ids:
        total_stmt = total_stmt.where(Customer.ftth64_id.in_(filters.ftth64_ids))

    if filters.agent_ids:
        total_stmt = total_stmt.where(Village.agent_id.in_(filters.agent_ids))

    total_amount = session.exec(total_stmt).one() or 0
        

    return BillFilterResponse(
        data=data,
        total_amount=total_amount
    )