from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.db.session import get_session
from app.models.lookup.package import Package
from app.schemas.package import (
    PackageCreate,
    PackageRead,
    PackageUpdate
)

router = APIRouter(
    prefix="/package",
    tags=["Package"]
    )


@router.get("/", response_model=list[PackageRead])
def list_packages(
    session: Session = Depends(get_session)
):
    packages = session.exec(select(Package)).all()
    return packages


@router.get("/{package_id}", response_model=PackageRead)
def get_package(
    package_id: int,
    session: Session = Depends(get_session)
):
    package = session.get(Package, package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return package


@router.post("/", response_model=PackageRead)
def create_package(
    payload: PackageCreate,
    session: Session = Depends(get_session)
                        ):
    package = Package.model_validate(payload)
    session.add(package)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Invalid reference or duplicate package data"
        )
    session.refresh(package)
    return package


@router.patch("/{package_id}", response_model=PackageRead)
def update_package(
    package_id: int,
    payload: PackageUpdate,
    session: Session = Depends(get_session)
):
    package = session.get(Package, package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(package, key, value)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
                            status_code=409,
                            detail="Invalid reference or duplicate package data"
                            )

    session.refresh(package)
    return package