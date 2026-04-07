from sqlmodel import Session, select

from app.models.core_models.customer import Customer

def get_customer_by_public_id(session: Session, customer_public_id: str) -> Customer:
    customer = session.exec(
        select(Customer).where(Customer.public_id == customer_public_id)
    ).first() 

    if not customer:
        raise ValueError("Customer not found")
    
    return customer