from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.db.session import get_session
from app.services.devices.device_info import build_deviceinfo_read
from app.models.lookup.status import Status
from app.models.core_models.customer import Customer
from app.dependencies.auth import get_current_user
from app.models.core_models.user import User
from app.models.lookup.tv_type import TVType
from app.models.lookup.village import Village
from app.services.customer.enforce_customer_vis import enforce_customer_visibility
from app.models.devices.device_info import DeviceInfo
from app.schemas.device_info import (
    DeviceInfoCreate,
    DeviceInfoRead,
    DeviceInfoUpdate
)

router = APIRouter(
    prefix="/device_info",
    tags=["DeviceInfo"],
    dependencies=[Depends(get_current_user)]
    )


@router.get("/", response_model=list[DeviceInfoRead])
def list_device_info(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(DeviceInfo)
        .join(Customer, Customer.id == DeviceInfo.customer_id)
        .join(Village, Village.id == Customer.village_id)
    )

    # enforce restriction at DB level
    if current_user.role == "agent":
        stmt = stmt.where(Village.agent_id == current_user.id)

    devices = session.exec(stmt).all()
    return [build_deviceinfo_read(d) for d in devices]


@router.get("/{device_info_public_id}", response_model=DeviceInfoRead)
def get_device_info(
    device_info_public_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    device = session.exec(
        select(DeviceInfo).where(DeviceInfo.public_id == device_info_public_id)
    ).first()

    if not device:
        raise HTTPException(status_code=404, detail="DeviceInfo not found")

    customer = session.get(Customer, device.customer_id)
    if not customer:
        raise HTTPException(500, "Customer not found for device")

    enforce_customer_visibility(
        customer=customer,
        current_user=current_user,
        session=session,
    )

    return build_deviceinfo_read(device)


@router.post("/", response_model=DeviceInfoRead)
def create_device_info(
    payload: DeviceInfoCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
                        ):
    customer = session.exec(
            select(Customer)
            .where(
                Customer.public_id == payload.customer_public_id
                )
    ).first()

    if not customer:
        raise HTTPException(404, "Customer not found")

    enforce_customer_visibility(
        customer=customer,
        current_user=current_user,
        session=session)

    # Explicit ORM construction (NO model_validate)
    device_info = DeviceInfo(
        customer_id=customer.id,
        account_number=payload.account_number,
        stb_id=payload.stb_id,
        vc_number=payload.vc_number,
        previous_vc_number=payload.previous_vc_number,
        tv_name=payload.tv_name,
        tvtype_id=payload.tvtype_id,
        status_id=payload.status_id,
    )

    session.add(device_info)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Invalid reference or duplicate device_info data"
        )
    session.refresh(device_info)
    return build_deviceinfo_read(device_info)


@router.patch("/{device_info_public_id}", response_model=DeviceInfoRead)
def update_device_info(
    device_info_public_id: str,
    payload: DeviceInfoUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    device_info = session.exec(
        select(DeviceInfo).where(DeviceInfo.public_id == device_info_public_id)
    ).one_or_none()

    if not device_info:
        raise HTTPException(status_code=404, detail="DeviceInfo not found")

    customer = session.get(Customer, device_info.customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")

    enforce_customer_visibility(
        customer=customer,
        current_user=current_user,
        session=session)

    update_data = payload.model_dump(exclude_unset=True)

    # Optional reference validation
    if "status_id" in update_data:
        if not session.get(Status, update_data["status_id"]):
            raise HTTPException(status_code=400, detail="Invalid status")

    if "tvtype_id" in update_data:
        if not session.get(TVType, update_data["tvtype_id"]):
            raise HTTPException(status_code=400, detail="Invalid TV type")

    for key, value in update_data.items():
        setattr(device_info, key, value)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
                            status_code=409,
                            detail="Invalid reference or duplicate"
                                   "device_info data"
                            )

    session.refresh(device_info)
    return build_deviceinfo_read(device_info)
