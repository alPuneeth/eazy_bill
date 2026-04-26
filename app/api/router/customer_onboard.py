import logging

from app.services.customer.delete_customer import delete_customer_service
logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.pagination.pag_response import PaginatedResponse
from app.services.customer.single_query_build import build_customer_onboard_list
from app.services.customer_onboard import onboard_single_customer
from app.dependencies.rbac import require_admin
from app.services.pagination.paginate_func import paginate
from app.schemas.customers.bulk_onboard import (
    CustomerOnboardBulkCreate,
    CustomerOnboardRead,
    CustomerOnboardBulkRead
    )
from app.services.customer.get_cus_by_public_id import get_customer_by_public_id
from app.services.customer.customer_onboard_public_id import (
    build_customer_onboard_read,
    patch_customer_onboard
    )
from app.models.core_models.customer import Customer
from app.models.core_models.user import User
from app.services.customer.customer_list import build_customer_list_query
from app.dependencies.rbac import get_current_user

from app.schemas.customers.customer_onboard import (
    CustomerOnboardCreate,
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
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
    ):
    return build_customer_onboard_list(session, current_user)


# ACTIVE + INACTIVE - card view
@router.get("/",
            response_model=PaginatedResponse[CustomerListRead],
            summary="List active and inactive customers")
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        # base query
        stmt = build_customer_list_query(
            device_statuses=["active", "inactive"],
            current_user=current_user
        )

        total, items = paginate(stmt, session, page, page_size, CustomerListRead)

        logger.info(
            "Customer list paginated",
            extra={
                "user_id": current_user.id,
                "page": page,
                "page_size": page_size
            }
            )

        # response
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }
    
    except Exception:
        logger.exception(
        "Failed to list customers",
        extra={
            "user_id": current_user.id,
            "page": page,
            "page_size": page_size
        }
    )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# ARCHIVED - card view
@router.get(
    "/archived",
    response_model=PaginatedResponse[CustomerListRead],
    summary="List archived customers"
)
def list_archived_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try: 
        stmt = build_customer_list_query(
            device_statuses=["archived"],
            current_user=current_user
        )

        total, items = paginate(stmt, session, page, page_size, CustomerListRead)

        logger.info(
        "Archived customers paginated",
        extra={
            "user_id": current_user.id,
            "page": page,
            "page_size": page_size
        }
        )
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }
    
    except Exception:
        logger.exception(
        "Failed to list archived customers",
        extra={
            "user_id": current_user.id,
            "page": page,
            "page_size": page_size
        }
    )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
            )


# GET ONE -single payload
@router.get("/{customer_public_id}", response_model=CustomerOnboardRead)
def get_customer(
    customer_public_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        customer = get_customer_by_public_id(session, customer_public_id)
    
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    return build_customer_onboard_read(customer.public_id, session, current_user)


# POST - single payload
@router.post("/", response_model=CustomerOnboardRead)
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
    return build_customer_onboard_read(customer.public_id, session, current_user)


@router.post("/bulk",
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
                build_customer_onboard_read(customer.public_id, session, current_user)
            )

        except (ValueError, PermissionError, IntegrityError) as e:
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
    try:
        customer = patch_customer_onboard(customer_public_id, payload, session, current_user)
        session.commit()
        session.refresh(customer)

    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(e))

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Constraint violation")

    return build_customer_onboard_read(customer.public_id, session, current_user)


@router.delete("/{customer_public_id}")
def delete_customer(
    customer_public_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    try:
        delete_customer_service(customer_public_id, session, current_user)
        session.commit() 

    except ValueError:
        session.rollback()
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}