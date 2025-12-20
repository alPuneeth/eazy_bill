from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.db.session import get_session
from app.models.devices.device_info import DeviceInfo
from app.schemas.device_info import (
    DeviceInfoCreate,
    DeviceInfoRead,
    DeviceInfoUpdate
)

router = APIRouter(
    prefix="/device_info",
    tags=["DeviceInfo"]
    )


@router.get("/", response_model=list[DeviceInfoRead])
def list_device_info(
    session: Session = Depends(get_session)
):
    device_info = session.exec(select(DeviceInfo)).all()
    return device_info


@router.get("/{device_info_id}", response_model=DeviceInfoRead)
def get_device_info(
    device_info_id: int,
    session: Session = Depends(get_session)
):
    device_info = session.get(DeviceInfo, device_info_id)
    if not device_info:
        raise HTTPException(status_code=404, detail="DeviceInfo not found")
    return device_info


@router.post("/", response_model=DeviceInfoRead)
def create_device_info(
    payload: DeviceInfoCreate,
    session: Session = Depends(get_session)
                        ):
    device_info = DeviceInfo.model_validate(payload)
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
    return device_info


@router.patch("/{device_info_id}", response_model=DeviceInfoRead)
def update_device_info(
    device_info_id: int,
    payload: DeviceInfoUpdate,
    session: Session = Depends(get_session)
):
    device_info = session.get(DeviceInfo, device_info_id)
    if not device_info:
        raise HTTPException(status_code=404, detail="DeviceInfo not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(device_info, key, value)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
                            status_code=409,
                            detail="Invalid reference or duplicate device_info data"
                            )

    session.refresh(device_info)
    return device_info