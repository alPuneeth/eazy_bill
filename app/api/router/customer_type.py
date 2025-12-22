from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.dependencies.rbac import require_admin
from app.db.session import get_session
from app.models.lookup.customer_type import CustomerType
from app.schemas.lookup.customer_type import (
    CustomerTypeCreate,
    CustomerTypeRead,
    CustomerTypeUpdate
)

router = APIRouter(
    prefix="/customer_type",
    tags=["CustomerType"],
    dependencies=[Depends(require_admin)]
    )


@router.get("/", response_model=list[CustomerTypeRead])
def list_customer_types(
    session: Session = Depends(get_session)
):
    customer_types = session.exec(select(CustomerType)).all()
    return customer_types


@router.get("/{customer_type_public_id}", response_model=CustomerTypeRead)
def get_customer_type(
    customer_type_public_id: str,
    session: Session = Depends(get_session)
):
    customer_type = session.exec(
        select(CustomerType).where(CustomerType.public_id == customer_type_public_id)
    ).first()

    if not customer_type:
        raise HTTPException(status_code=404, detail="CustomerType not found")
    return customer_type


@router.post("/", response_model=CustomerTypeRead)
def create_customer_type(
    payload: CustomerTypeCreate,
    session: Session = Depends(get_session)
                        ):
    customer_type = CustomerType.model_validate(payload)
    session.add(customer_type)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="CustomerType with this name already exists"
             )

    session.refresh(customer_type)
    return customer_type


@router.patch("/{customer_type_public_id}", response_model=CustomerTypeRead)
def update_customer_type(
    customer_type_public_id: str,
    payload: CustomerTypeUpdate,
    session: Session = Depends(get_session)
):
    customer_type = session.exec(
        select(CustomerType).where(CustomerType.public_id == customer_type_public_id)
    ).first()

    if not customer_type:
        raise HTTPException(status_code=404, detail="CustomerType not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer_type, key, value)

    session.commit()
    session.refresh(customer_type)
    return customer_type