from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.dependencies.rbac import get_current_user
from app.db.session import get_session

from app.models.core_models.user import User

from app.schemas.bill import (
    BillCreate,
    BillRead,
    BillUpdate
)

from app.services.exceptions import VillageAccessDeniedError
from app.services.bill.bill_gen_code_vill import generate_bill_code_for_village
from app.services.bill.bills_list import get_all_bills
from app.services.bill.bill_exceptions import (
    BillNotFoundError,
    OverlappinBillingPeriod,
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
from app.services.bill.bill_by_customer import get_blls_by_customer


router = APIRouter(
    prefix="/bill",
    tags=["Bill"]
    )


# all bills
@router.get("/", response_model=list[BillRead])
def list_bills(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Thin router responsibilities:
    - Dependency injection
    - Exception translation
    - No business logic
    """
    try:
        return get_all_bills(
            session=session,
            current_user=current_user
            )

    except PermissionError:
        # Translate domain/system error → HTTP
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access bills"
        )
    
    except Exception:
        # Optional: fallback safeguard (log in real apps)
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
    
    except OverlappinBillingPeriod:
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
            "Bills cannot be modified after the day of creation"
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
    response_model=list[BillRead]
)
def get_bills_by_customer(
    customer_public_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Thin router:
    - Delegates to service
    - Handles only HTTP concerns
    """
    try:
        return get_blls_by_customer(
            customer_public_id=customer_public_id,
            session=session,
            current_user=current_user
        )

    except CustomerNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    except Exception:
        # Optional safety fallback (log in real apps)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )