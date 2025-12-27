from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select as orm_select
from sqlalchemy.exc import IntegrityError

from app.db.session import get_session
from app.services.customer.customer_onboard_public_id import (
    build_customer_onboard_read,
    patch_customer_onboard
    )
from app.services.customer.customer_orm import (
    build_customer_onboard_read_from_customer
    )
from app.models.core_models.customer import Customer
# from app.models.bill.bill import Bill
from app.models.devices.device_info import DeviceInfo
from app.models.lookup.village import Village
from app.models.lookup.customer_type import CustomerType
from app.models.lookup.package import Package
from app.models.lookup.ftth64 import FTTH64
from app.models.lookup.status import Status
from app.models.lookup.tv_type import TVType
# from app.models.lookup.status import StatusEnum

from app.services.customer.customer_list import build_customer_list_query

from app.schemas.customers.customer_onboard import (
    CustomerOnboardCreate,
    CustomerOnboardRead,
    CustomerOnboardUpdate,
    CustomerListRead

)

router = APIRouter(
    prefix="/customer",
    tags=["Customer"]
    )


# get customers - active + inactive + archived
@router.get(
        "/all",
        response_model=list[CustomerOnboardRead],
        summary="List all customers"
            )
def list_all_customers(
    session: Session = Depends(get_session)
):
    customers = session.exec(
        orm_select(Customer)
    ).all()
    return [build_customer_onboard_read_from_customer(customer, session)
            for customer in customers]


# ACTIVE + INACTIVE - card view
@router.get("/", response_model=list[CustomerListRead],
                 summary="List active and inactive customers")
def list_customers(
    session: Session = Depends(get_session)
):
    stmt = build_customer_list_query(
        device_statuses=["active", "inactive"]
    )
    return session.exec(stmt).mappings().all()


# ARCHIVED - card view
@router.get(
    "/archived",
    response_model=list[CustomerListRead],
    summary="List archived customers"
)
def list_archived_customers(
    session: Session = Depends(get_session)
):
    stmt = build_customer_list_query(
        device_statuses=["archived"]
    )
    return session.exec(stmt).mappings().all()


# GET ONE -single payload
@router.get("/{customer_public_id}", response_model=CustomerOnboardRead)
def get_customer(
    customer_public_id: str,
    session: Session = Depends(get_session)
):
    customer = session.exec(
        orm_select(Customer).where(Customer.public_id == customer_public_id)
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return build_customer_onboard_read(customer_public_id, session)


# POST - single payload
@router.post("/create", response_model=CustomerOnboardRead)
def create_customer(
    payload: CustomerOnboardCreate,
    session: Session = Depends(get_session)
):
    try:
        if not session.get(Village, payload.village_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid village"
                                )
        if not session.get(CustomerType, payload.customer_type_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid customer type"
                                )
        if not session.get(FTTH64, payload.ftth64_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid FTTH64"
                                )
        if not session.get(Package, payload.package_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid package"
                                )
        if not session.get(Status, payload.status_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
                                )
        if not session.get(TVType, payload.tvtype_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TV type"
                                )

        customer = Customer(
            name=payload.name,
            phone=payload.phone,
            alternate_number=payload.alternate_number,
            aadhaar_number=payload.aadhaar_number,
            upi_id=payload.upi_id,
            village_id=payload.village_id,
            customer_type_id=payload.customer_type_id,
            ftth64_id=payload.ftth64_id,
            package_id=payload.package_id,
            description=payload.description
        )
        session.add(customer)
        session.flush()  # customer.id is now available

        if customer.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create customer"
            )

        device_info = DeviceInfo(
            customer_id=customer.id,
            account_number=payload.account_number,
            stb_id=payload.stb_id,
            vc_number=payload.vc_number,
            previous_vc_number=payload.previous_vc_number,
            tvtype_id=payload.tvtype_id,
            status_id=payload.status_id,
            tv_name=payload.tv_name
        )
        session.add(device_info)

        session.commit()
        session.refresh(customer)

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate or constraint violation"
        )
    return build_customer_onboard_read(customer.public_id, session)


# PATCH - single payload
@router.patch("/{customer_public_id}", response_model=CustomerOnboardRead)
def update_customer(
    customer_public_id: str,
    payload: CustomerOnboardUpdate,
    session: Session = Depends(get_session),
):
    try:
        patch_customer_onboard(customer_public_id, payload, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Constraint violation")

    return build_customer_onboard_read(customer_public_id, session)

 