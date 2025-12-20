from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.db.session import get_session
from app.models.bill.subscription import Subscription
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionUpdate
)

router = APIRouter(
    prefix="/subscription",
    tags=["Subscription"]
    )


@router.get("/", response_model=list[SubscriptionRead])
def list_subscriptions(
    session: Session = Depends(get_session)
):
    subscriptions = session.exec(select(Subscription)).all()
    return subscriptions


@router.get("/{subscription_id}", response_model=SubscriptionRead)
def get_subscription(
    subscription_id: int,
    session: Session = Depends(get_session)
):
    subscription = session.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.post("/", response_model=SubscriptionRead)
def create_subscription(
    payload: SubscriptionCreate,
    session: Session = Depends(get_session)
                        ):
    subscription = Subscription.model_validate(payload)
    session.add(subscription)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate or invalid subscription"
             )

    session.refresh(subscription)
    return subscription


@router.patch("/{subscription_id}", response_model=SubscriptionRead)
def update_subscription(
    subscription_id: int,
    payload: SubscriptionUpdate,
    session: Session = Depends(get_session)
):
    subscription = session.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
                            status_code=400,
                            detail="No fields provided for update"
                            )
    
    for key, value in update_data.items():
        setattr(subscription, key, value)

    try:
        session.commit()
        
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Invalid subscription update"
        )
    
    session.refresh(subscription)
    return subscription