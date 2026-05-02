from datetime import datetime
from sqlmodel import select, Session
from sqlalchemy import func

from app.models.core_models.customer import Customer
from app.models.lookup.village import Village
from app.models.bill.bill import Bill
from app.models.core_models.user import User


def generate_bill_code(village: Village, session: Session, current_user: User):
    """
    returns a new bill_code if there are no previous bills for a Customer else 
    the bill_code from the latest bill is incremented by 1

    Args:
    village - Village ORM
    session - to interact with the DB

    Raises:
    Domain exceptions - for data not found

    """
    current_year = datetime.now().year   
    current_year_short = current_year % 100

    start = datetime(current_year, 1, 1)  # 2026-01-01 00:00:00
    end = datetime(current_year + 1, 1, 1) # 2027-01-01 00:00:00

    # Fetch latest bill for this village in current year
    latest_bill = session.exec(
        select(Bill.bill_code)
        .join(Customer, Bill.customer_id == Customer.id)
        .where(
            Customer.village_id == village.id,
            Bill.bill_date >= start,
            Bill.bill_date < end
        )
        .order_by(Bill.id.desc())
        .limit(1)
    ).first()

    vill_code = village.village_code.upper()

    if not latest_bill:
        return f"{vill_code}{current_user.user_code}{current_year_short:02d}-001"
    
    bill_code: str = latest_bill

    # Parse and increment counter
    try:
        last_counter = int(bill_code.split("-")[-1])

    except (ValueError, IndexError):
        last_counter = 0

    next_counter = last_counter + 1
    return f"{vill_code}{current_user.user_code}{current_year_short:02d}-{next_counter:03d}"
