from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.db.session import get_session
from app.models.core_models.customer import Customer
from app.models.devices.device_info import DeviceInfo
from app.models.lookup.village import Village
from app.models.lookup.customer_type import CustomerType
from app.models.lookup.package import Package
from app.models.lookup.ftth64 import FTTH64
from app.models.lookup.status import StatusEnum, Status
from app.models.lookup.tv_type import TVType

from app.schemas.customers.customer_domain import (
    CustomerCreate,
    CustomerRead,
    CustomerUpdate
)

# from app.models.devices.device_info import DeviceInfo
# from app.dependencies.rbac import require_admin


router = APIRouter(
    prefix="/customer/domain",
    tags=["Customer"]
    )


# STATIC ROUTES FIRST
# List of ACTIVE customers
@router.get(
        "/active",
        response_model=list[CustomerRead],
        summary="List active customers"
        )
def list_active_customers(
    session: Session = Depends(get_session)
):
    active_status = session.exec(
        select(Status).where(Status.name == StatusEnum.ACTIVE)
    ).one()

    stmt = (
            select(Customer)
            .join(DeviceInfo)
            .where(DeviceInfo.status_id == active_status.id)
            .distinct()
            )

    customers = session.exec(stmt).all()

    return customers


# List of INACTIVE customers
@router.get(
        "/inactive",
        response_model=list[CustomerRead],
        summary="List inactive customers"
        )
def list_inactive_customers(
    session: Session = Depends(get_session)
):

    inactive_status = session.exec(
        select(Status).where(Status.name == StatusEnum.INACTIVE)
    ).one()

    stmt = (
            select(Customer)
            .join(DeviceInfo)
            .where(DeviceInfo.status_id == inactive_status.id)
            .distinct()
            )

    customers = session.exec(stmt).all()

    return customers


# List of ARCHIVED customers
@router.get(
        "/archive",
        response_model=list[CustomerRead],
        summary="List archive customers"
        )
def list_archive_customers(
    session: Session = Depends(get_session)
):
    archived_status = session.exec(
        select(Status).where(Status.name == StatusEnum.ARCHIVED)
    ).one()

    stmt = (
            select(Customer)
            .join(DeviceInfo)
            .where(DeviceInfo.status_id == archived_status.id)
            .distinct()
            )

    customers = session.exec(stmt).all()

    return customers


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
                            detail="Invalid reference or"
                            "duplicate customer data"
                            )

    session.refresh(customer)
    return customer