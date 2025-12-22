from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.db.session import get_session
from app.models.core_models.customer import Customer
from app.schemas.customer import (
    CustomerCreate,
    CustomerRead,
    CustomerUpdate
)

from app.models.devices.device_info import DeviceInfo
from app.dependencies.rbac import require_admin


router = APIRouter(
    prefix="/customer",
    tags=["Customer"],
    dependencies=[Depends(require_admin)]
    )


# STATIC ROUTES FIRST
@router.get(
        "/active",
        response_model=list[CustomerRead],
        summary="List active customers"
        )
def list_active_customers(
    session: Session = Depends(get_session)
):
    ACTIVE_STATUS_ID = 1
    stmt = (
        select(Customer)
        .join(DeviceInfo)
        .where(DeviceInfo.status_id == ACTIVE_STATUS_ID)
        .distinct()
        )

    return session.exec(stmt).all()


@router.get(
        "/inactive",
        response_model=list[CustomerRead],
        summary="List inactive customers"
        )
def list_inactive_customers(
    session: Session = Depends(get_session)
):
    INACTIVE_STATUS_ID = 2
    stmt = (
        select(Customer)
        .join(DeviceInfo)
        .where(DeviceInfo.status_id == INACTIVE_STATUS_ID)
        .distinct()
        )

    return session.exec(stmt).all()


@router.get(
        "/archive",
        response_model=list[CustomerRead],
        summary="List archive customers"
        )
def list_archive_customers(
    session: Session = Depends(get_session)
):
    ARCHIVE_STATUS_ID = 3
    stmt = (
        select(Customer)
        .join(DeviceInfo)
        .where(DeviceInfo.status_id == ARCHIVE_STATUS_ID)
        .distinct()
        )

    return session.exec(stmt).all()


@router.get("/", response_model=list[CustomerRead])
def list_customers(
    session: Session = Depends(get_session)
):
    customers = session.exec(select(Customer)).all()
    return customers


@router.post("/", response_model=CustomerRead)
def create_customer(
    payload: CustomerCreate,
    session: Session = Depends(get_session)
                        ):
    customer = Customer.model_validate(payload)
    session.add(customer)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Invalid reference or duplicate customer data"
        )
    session.refresh(customer)
    return customer


# DYNAMIC ROUTES LAST
@router.get("/{customer_public_id}", response_model=CustomerRead)
def get_customer(
    customer_public_id: str,
    session: Session = Depends(get_session)
):
    customer = session.exec(
        select(Customer).where(Customer.public_id == customer_public_id)
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.patch("/{customer_public_id}", response_model=CustomerRead)
def update_customer(
    customer_public_id: str,
    payload: CustomerUpdate,
    session: Session = Depends(get_session)
):
    customer = session.exec(
        select(Customer).where(Customer.public_id == customer_public_id)
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
                            status_code=409,
                            detail="Invalid reference or duplicate customer data"
                            )

    session.refresh(customer)
    return customer