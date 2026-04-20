from sqlmodel import Session, select
from sqlmodel import desc

from app.models.bill.bill import Bill
from app.models.core_models.customer import Customer
from app.models.lookup.package import Package
from app.models.core_models.user import User

from app.services.bill.bill_exceptions import CustomerNotFoundError
from app.services.customer.enforce_customer_vis import enforce_customer_visibility


def build_bills_by_customer_query(
    customer_public_id: str,
    current_user: User,
    session: Session
):
    # 1. Resolve customer
    customer = session.exec(
        select(Customer).where(Customer.public_id == customer_public_id)
    ).one_or_none()

    if not customer:
        raise CustomerNotFoundError()

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
            User.public_id.label("created_by_public_id"),
            User.name.label("created_by_name"),

            Bill.created_at,
            Bill.updated_at,
        )
        .join(Customer, Customer.id == Bill.customer_id)
        .join(Package, Package.id == Bill.package_id)
        .join(User, User.id == Bill.created_by_id)
        .where(Customer.id == customer.id)
        .order_by(desc(Bill.bill_date), desc(Bill.id))
    )

    return stmt