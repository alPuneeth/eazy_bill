from datetime import date
from sqlmodel import Session, select
from sqlalchemy import func, case

from app.models.bill.bill import Bill
from app.schemas.reports.collections import CollectionsSummaryRead
from app.models.core_models.user import User, UserRole
from app.models.lookup.village import Village
from app.models.core_models.customer import Customer


def get_collections_summary(session: Session, current_user: User) -> CollectionsSummaryRead:
    today = date.today()

    stmt = select(
        func.coalesce(
            func.sum(
                case(
                    (func.date(Bill.created_at) == today, Bill.bill_amount),
                    else_=0
                )
            ),
            0
        ).label("today_collection"),

        func.coalesce(
            func.sum(
                case(
                    (
                        func.date_trunc("month", Bill.created_at)
                        == func.date_trunc("month", func.current_date()),
                        Bill.bill_amount
                    ),
                    else_=0
                )
            ),
            0
        ).label("monthly_collection"),
    ).join(
        Customer, Bill.customer_id == Customer.id
        ).join(Village, Village.id == Customer.village_id
               )

    if current_user.role == UserRole.AGENT:
        stmt = stmt.where(Village.agent_id == current_user.id)

    result = session.exec(stmt).one()

    return CollectionsSummaryRead(
        today_collection=result.today_collection,
        monthly_collection=result.monthly_collection
    )
