from sqlmodel import Session, select

from app.models.bill.bill import Bill
from app.models.core_models.customer import Customer
from app.models.lookup.package import Package
from app.models.core_models.user import User
from app.schemas.reports.bill_by_agent import BillByAgentRead


def get_bills_created_by_agent(
    *,
    agent_public_id: str,
    session: Session
) -> list[BillByAgentRead]:

    stmt = (
        select(
            Bill.public_id.label("bill_public_id"),
            Bill.bill_code,
            Bill.bill_date,
            Bill.start_date,
            Bill.end_date,
            Bill.monthly_count,
            Bill.bill_amount,

            Customer.public_id.label("customer_public_id"),
            Customer.name.label("customer_name"),

            Package.name.label("package_name"),

            User.public_id.label("agent_public_id"),
            User.name.label("agent_name"),
        )
        .select_from(Bill)
        .join(User, User.id == Bill.created_by_id)
        .join(Customer, Customer.id == Bill.customer_id)
        .join(Package, Package.id == Bill.package_id)
        .where(User.public_id == agent_public_id)
        .order_by(Bill.bill_date.desc())
    )

    rows = session.exec(stmt).all()
    return [BillByAgentRead(**row._mapping) for row in rows]
