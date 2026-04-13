from fastapi import HTTPException, Depends
from sqlmodel import Session, select

from app.models.core_models.customer import Customer
from app.db.session import get_session
from app.models.core_models.user import User, UserRole
from app.models.lookup.village import Village


def enforce_customer_visibility(
    customer: Customer,
    current_user: User,
    session: Session
):
    if current_user.role == UserRole.ADMIN:
        return

    village = session.exec(
        select(Village).where(Village.id == customer.village_id)
    ).first()

    if not village:
        # defensive: should never happen if FK integrity is correct
        raise HTTPException(
            status_code=500,
            detail="Customer linked to invalid village"
        )

    if village.agent_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
