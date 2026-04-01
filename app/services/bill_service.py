from datetime import datetime
from fastapi import HTTPException, status
from sqlmodel import select, Session
from sqlalchemy import func

from app.models.core_models.customer import Customer
from app.models.bill.bill import Bill
from app.models.lookup.village import Village
from app.models.core_models.user import User


def generate_bill_code(village_id: int, session: Session, current_user: User):
    """
    returns a new bill_code if there are no previous bills for a Customer else 
    the bill_code from the latest bill is incremented by 1

    Args:
    village_id - integer ID of the village as stored in DB
    session - to interact with the DB

    Raises:
    HTTPException_404 - for data not found

    """
    current_year = datetime.now().year
    current_year_short = current_year % 100

    # Step 1: fetch Village
    village = session.get(Village, village_id)
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village not found"
        )

    # Step 2: Fetch latest bill for this village in current year
    latest_bill = session.exec(
        select(Bill)
        .join(Customer, Bill.customer_id == Customer.id)
        .where(
            Customer.village_id == village_id,
            func.extract("year", Bill.bill_date) == current_year
        )
        .order_by(Bill.bill_date.desc())
        .limit(1)
    ).first()

    if not latest_bill:
        return f"{village.village_code}{current_user.user_code}{current_year_short:02d}-001"

    # Step 3: Parse and increment counter

    try:
        last_counter = int(latest_bill.bill_code.split("-")[-1])

    except (ValueError, IndexError):
        last_counter = 0

    next_counter = last_counter + 1
    return f"{village.village_code}{current_user.user_code}{current_year_short:02d}-{next_counter:03d}"
