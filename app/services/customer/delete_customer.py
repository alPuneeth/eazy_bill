from sqlmodel import Session, select

from app.models.core_models.customer import Customer
from app.models.core_models.user import User
from app.models.devices.device_info import DeviceInfo
from app.models.lookup.status import Status, StatusEnum


class CustomerNotFoundError(Exception):
    """Raised only when the requested customer does not exist (maps to HTTP 404)."""


def delete_customer_service(
        customer_public_id: str,
        session: Session,
        current_user: User
):
    customer = session.exec(
        select(Customer).where(Customer.public_id == customer_public_id)
    ).first()

    if not customer:
        raise CustomerNotFoundError("Customer not found")
    
    device = session.exec(
        select(DeviceInfo).where(DeviceInfo.customer_id == customer.id)
    ).first()

    if not device:
        # invariant violation: every customer must have exactly one device
        raise RuntimeError("Customer has no device")
    
    archived_status = session.exec(
        select(Status).where(Status.name == StatusEnum.ARCHIVED)
    ).first()

    if not archived_status:
        raise RuntimeError("ARCHIVED status not configured")
    
    device.status_id = archived_status.id   
    return customer