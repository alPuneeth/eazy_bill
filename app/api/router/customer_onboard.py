from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select as orm_select
from sqlalchemy.exc import IntegrityError

from app.db.session import get_session
from app.services.customer.single_query_build import build_customer_onboard_list
from app.services.customer.enforce_customer_vis import enforce_customer_visibility
from app.services.customer_onboard import onboard_single_customer
from app.schemas.customers.bulk_onboard import (
    CustomerOnboardBulkCreate,
    CustomerOnboardRead,
    CustomerOnboardBulkRead
    )
from app.services.customer.customer_onboard_public_id import (
    build_customer_onboard_read,
    patch_customer_onboard
    )
# from app.services.customer.customer_orm import (
#     build_customer_onboard_read_from_customer
#     )
from app.models.core_models.customer import Customer
from app.models.core_models.user import User
from app.services.customer.customer_list import build_customer_list_query
from app.dependencies.rbac import get_current_user
from app.dependencies.rbac import require_admin

from app.schemas.customers.customer_onboard import (
    CustomerOnboardCreate,
    CustomerOnboardRead,
    CustomerOnboardUpdate,
    CustomerListRead

)

router = APIRouter(
    prefix="/customer",
    tags=["Customer"],
    dependencies=[Depends(get_current_user)]
    )


# get customers - active + inactive + archived
@router.get(
        "/all",
        response_model=list[CustomerOnboardRead],
        summary="List all customers",
        dependencies=[Depends(require_admin)]
            )
def list_all_customers(
    session: Session = Depends(get_session)
):
    return build_customer_onboard_list(session)


# ACTIVE + INACTIVE - card view
@router.get("/", response_model=list[CustomerListRead],
            summary="List active and inactive customers")
def list_customers(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = build_customer_list_query(
        device_statuses=["active", "inactive"],
        current_user=current_user
    )
    return session.exec(stmt).mappings().all()


# ARCHIVED - card view
@router.get(
    "/archived",
    response_model=list[CustomerListRead],
    summary="List archived customers"
)
def list_archived_customers(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = build_customer_list_query(
        device_statuses=["archived"],
        current_user=current_user
    )
    return session.exec(stmt).mappings().all()


# GET ONE -single payload
@router.get("/{customer_public_id}", response_model=CustomerOnboardRead)
def get_customer(
    customer_public_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    customer = session.exec(
        orm_select(Customer).where(Customer.public_id == customer_public_id)
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    enforce_customer_visibility(customer, current_user, session)

    return build_customer_onboard_read(customer_public_id, session)


# POST - single payload
@router.post("/create", response_model=CustomerOnboardRead)
def create_customer(
    payload: CustomerOnboardCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        customer = onboard_single_customer(
            payload=payload,
            session=session,
            current_user=current_user
        )

        session.commit()
        session.refresh(customer)

    except PermissionError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agents cannot create customers in restricted villages"
        )

    except ValueError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate or constraint violation"
        )
    return build_customer_onboard_read(customer.public_id, session)


@router.post("/create/bulk",
             response_model=CustomerOnboardBulkRead
             )
def create_customers_bulk(
    payload: CustomerOnboardBulkCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    success = []
    failed = []

    for index, customer_payload in enumerate(payload.customers):
        try:
            customer = onboard_single_customer(
                payload=customer_payload,
                session=session,
                current_user=current_user
            )

            session.commit()
            session.refresh(customer)

            success.append(
                build_customer_onboard_read(customer.public_id, session)
            )

        except Exception as e:
            session.rollback()
            failed.append({
                "index": index,
                "name": customer_payload.name,
                "phone": customer_payload.phone,
                "reason": str(e)
            })

    return {
        "success": success,
        "failed": failed
    }


# PATCH - single payload
@router.patch("/{customer_public_id}", response_model=CustomerOnboardRead)
def update_customer(
    customer_public_id: str,
    payload: CustomerOnboardUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    customer = session.exec(orm_select(Customer)
                            .where(
                                Customer.public_id == customer_public_id
                                )
                            ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    enforce_customer_visibility(customer, current_user, session)

    try:
        patch_customer_onboard(customer_public_id, payload, session)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Constraint violation")

    return build_customer_onboard_read(customer_public_id, session)
