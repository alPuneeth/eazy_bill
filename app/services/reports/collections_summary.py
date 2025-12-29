from datetime import date
from sqlmodel import Session, select
from sqlalchemy import func, case

from app.models.bill.bill import Bill
from app.schemas.reports.collections import CollectionsSummaryRead


def get_collections_summary(session: Session) -> CollectionsSummaryRead:
    today = date.today()

    stmt = select(
        func.coalesce(
            func.sum(
                case(
                    (Bill.bill_date == today, Bill.bill_amount),
                    else_=0
                )
            ),
            0
        ).label("today_collection"),

        func.coalesce(
            func.sum(
                case(
                    (
                        func.date_trunc("month", Bill.bill_date)
                        == func.date_trunc("month", today),
                        Bill.bill_amount
                    ),
                    else_=0
                )
            ),
            0
        ).label("monthly_collection"),
    )

    result = session.exec(stmt).one()

    return CollectionsSummaryRead(
        today_collection=result.today_collection,
        monthly_collection=result.monthly_collection
    )
