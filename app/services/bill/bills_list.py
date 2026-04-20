from sqlmodel import Session, select
from sqlalchemy import desc

from app.models.lookup.village import Village
from app.models.core_models.user import User, UserRole
from app.models.core_models.customer import Customer
from app.models.lookup.package import Package
from app.models.bill.bill import Bill

from app.schemas.common import IdValueRead, CreatorSummary
from app.schemas.bill import BillRead

from app.services.bill.bill_visibility import apply_bill_visibility
from app.services.bill.bill_mapper import map_bill_row


def build_bill_list_query(current_user: User):
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
        .join(Village, Village.id == Customer.village_id)
        .join(Package, Package.id == Bill.package_id)
        .join(User, User.id == Bill.created_by_id)
        .order_by(desc(Bill.bill_date), desc(Bill.id))
    )

    # 🔐Apply RBAC filter
    stmt = apply_bill_visibility(stmt, current_user)

    return stmt

    


    