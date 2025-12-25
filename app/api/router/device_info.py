from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.db.session import get_session
from app.services.devices.device_info import build_deviceinfo_read
from app.models.lookup.status import Status
from app.models.lookup.tv_type import TVType
from app.dependencies.rbac import require_admin
from app.models.devices.device_info import DeviceInfo
from app.schemas.device_info import (
    DeviceInfoCreate,
    DeviceInfoRead,
    DeviceInfoUpdate
)

router = APIRouter(
    prefix="/device_info",
    tags=["DeviceInfo"],
    dependencies=[Depends(require_admin)]
    )


@router.get("/", response_model=list[DeviceInfoRead])
def list_device_info(
    session: Session = Depends(get_session)
):
    devices = session.exec(select(DeviceInfo)).all()
    return [build_deviceinfo_read(d) for d in devices]


@router.get("/{device_info_public_id}", response_model=DeviceInfoRead)
def get_device_info(
    device_info_public_id: str,
    session: Session = Depends(get_session)
):
    device_info = session.exec(
        select(DeviceInfo).where(DeviceInfo.public_id == device_info_public_id)
    ).first()

    if not device_info:
        raise HTTPException(status_code=404, detail="DeviceInfo not found")
    return build_deviceinfo_read(device_info)


@router.post("/", response_model=DeviceInfoRead)
def create_device_info(
    payload: DeviceInfoCreate,
    session: Session = Depends(get_session)
                        ):

    # Explicit ORM construction (NO model_validate)
    device_info = DeviceInfo(
        customer_id=payload.customer_id,
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
    session: Session = Depends(get_session)
):
    device_info = session.exec(
        select(DeviceInfo).where(DeviceInfo.public_id == device_info_public_id)
    ).first()
    if not device_info:
        raise HTTPException(status_code=404, detail="DeviceInfo not found")

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
