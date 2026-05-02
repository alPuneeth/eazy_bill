import logging
logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.dependencies.rbac import get_current_user
from app.db.session import get_session

from app.models.core_models.user import User

from app.schemas.bill import (
    BillCreate,
    BillRead,
    BillUpdate
)

from app.schemas.pagination.pag_response import PaginatedResponse
from app.services.exceptions import VillageAccessDeniedError
from app.services.bill.bill_gen_code_vill import generate_bill_code_for_village
from app.services.bill.bills_list import build_bill_list_query
from app.services.bill.bill_mapper import map_bill_row
from app.services.bill.bill_exceptions import (
    BillNotFoundError,
    OverlappingBillingPeriod,
    VillageNotFoundError,
    CustomerNotFoundError,
    InvalidPackageError,
    BillConflictError,
    EmptyUpdateError,
    BillUpdateNotAllowedError
)
from app.services.bill.bill_by_public_id import get_bill_by_public_id
from app.services.bill.bill_create import create_bll
from app.services.bill.bill_update import update_bll
from app.services.bill.bill_by_customer import build_bills_by_customer_query
from app.services.pagination.paginate_func import paginate


router = APIRouter(
    prefix="/bill",
    tags=["Bill"]
    )


# all bills
@router.get("/", response_model=PaginatedResponse[BillRead])
def list_bills(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        stmt = build_bill_list_query(current_user=current_user)

        total, items = paginate(stmt, session, page, page_size, map_bill_row)

        logger.info(
        "Paginated bill list",
        extra={
            "page": page,
            "page_size": page_size,
            "user_id": current_user.id
        }
    )

        return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }

    except PermissionError:
        # Translate domain/system error → HTTP
        logger.warning(
                        "Unauthorized access attempt",
                        extra={"user_id": current_user.id}
                    )

        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access bills"
        )
    
    except Exception:
        # Optional: fallback safeguard (log in real apps)
        logger.exception(
            "Failed to list bills",
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


@router.get("/generate_bill_code/{village_code}", response_model=str)
def get_bill_code(
    village_code: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
                  ):
    try:
        return generate_bill_code_for_village(
            village_code=village_code,
            session=session,
            current_user=current_user
        )
    
    except VillageNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Village not found"
        )

    except VillageAccessDeniedError:
        raise HTTPException(
            status_code=403,
            detail="Access to this village is restricted!"
        )


# bill
@router.get("/{bill_public_id}", response_model=BillRead)
def get_bill(
    bill_public_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Thin router:
    - Only HTTP concerns
    - Delegates to service
    - Translates exceptions
    """
    try:
        return get_bill_by_public_id(
            bill_public_id=bill_public_id,
            current_user=current_user,
            session=session)

    except BillNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Bill not found!"
        )


@router.post("/", response_model=BillRead)
def create_bill(
    payload: BillCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Thin router:
    - No DB logic
    - No business rules
    - Only exception translation
    """
    try:
        return create_bll(
            payload=payload,
            session=session,
            current_user=current_user
        )

    except CustomerNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    except InvalidPackageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid package"
        )

    except BillConflictError:
        raise HTTPException(
            status_code=409,
            detail="Duplicate bill_code or invalid bill"
        )
    
    except OverlappingBillingPeriod:
        raise HTTPException(
            status_code=409,
            detail="Billing period conflict: Please select a non-overlapping timeframe."
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


@router.patch("/{bill_public_id}", response_model=BillRead)
def update_bill(
    bill_public_id: str,
    payload: BillUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Thin router:
    - Delegates to service
    - Maps domain errors -> HTTP
    """
    try:
        return update_bll(
            bill_public_id=bill_public_id,
            payload=payload,
            session=session,
            current_user=current_user
        )
    
    except BillNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Bill not found"
        )
    
    except CustomerNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
    
    except InvalidPackageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid package"
        )
    
    except BillUpdateNotAllowedError:
        raise HTTPException(
            400,
            "Bills can only be modified on the bill date"
        )

    except EmptyUpdateError:
        raise HTTPException(
            400,
            "No fields provided for update"
        )

    except BillConflictError:
        raise HTTPException(
            409,
            "Duplicate bill_code or invalid foreign key"
        )

    except PermissionError:
        raise HTTPException(403, "Access denied")



# bill by customer public id
@router.get(
    "/customer/{customer_public_id}",
    response_model=PaginatedResponse[BillRead]
)
def get_bills_by_customer(
    customer_public_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        stmt = build_bills_by_customer_query(
            customer_public_id=customer_public_id,
            session=session,
            current_user=current_user
        )

        total, items = paginate(
            stmt,
            session,
            page,
            page_size,
            map_bill_row
        )

        logger.info(
                    "Paginated bills for customer",
                    extra={
                        "page": page,
                        "page_size": page_size,
                        "user_id": current_user.id
                    }
                )

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }


    except CustomerNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    except PermissionError:
        logger.warning(
        "Unauthorized access attempt",
        extra={
            "user_id": current_user.id,
            "customer_public_id": customer_public_id
        }
        )
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    except Exception:
        # Optional safety fallback (log in real apps)
        logger.exception("Failed to fetch bills by customer",
        extra={
                "customer_public_id": customer_public_id,
                "user_id": current_user.id
    })

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )