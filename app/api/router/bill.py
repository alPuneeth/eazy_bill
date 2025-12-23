from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.dependencies.rbac import require_admin, get_current_user
from app.models.core_models.user import User
from app.db.session import get_session
from app.models.bill.bill import Bill
from app.schemas.bill import (
    BillCreate,
    BillRead,
    BillUpdate
)

router = APIRouter(
    prefix="/bill",
    tags=["Bill"],
    dependencies=[Depends(require_admin)]
    )


@router.get("/", response_model=list[BillRead])
def list_bills(
    session: Session = Depends(get_session)
):
    
    bills = session.exec(select(Bill)).all()
    return bills


@router.get("/{bill_public_id}", response_model=BillRead)
def get_bill(
    bill_public_id: str,
    session: Session = Depends(get_session)
):
    bill = session.exec(
        select(Bill).where(Bill.public_id == bill_public_id)
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.post("/", response_model=BillRead)
def create_bill(
    payload: BillCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
                ):

    bill = Bill(
        **payload.model_dump(),
        created_by_id=current_user.id
    )

    session.add(bill)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate bill_code or invalid bill"
             )

    session.refresh(bill)
    return bill 


@router.patch("/{bill_public_id}", response_model=BillRead)
def update_bill(
    bill_public_id: str,
    payload: BillUpdate,
    session: Session = Depends(get_session)
):
    bill = session.exec(
        select(Bill).where(Bill.public_id == bill_public_id)
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )
    for key, value in update_data.items():
        setattr(bill, key, value)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=409,
            detail="Duplicate bill_code or invalid foreign key"
            )

    session.refresh(bill)
    return bill