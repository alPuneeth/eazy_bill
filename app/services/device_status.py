from datetime import datetime, timezone
from sqlmodel import Session, select
from app.models.bill.bill import Bill
from app.models.devices.device_info import DeviceInfo


def sync_device_status_from_bills(
    *,
    customer_id: int,
    session: Session,
    active_status_id: int,
    inactive_status_id: int,
):
    """
    Updates ALL devices of a customer based on bill period.
    """
    today = datetime.now(timezone.utc)

    has_active_bill = session.exec(
        select(Bill.id)
        .where(
            Bill.customer_id == customer_id,
            Bill.start_date <= today,
            Bill.end_date >= today,
        )
        .limit(1)
    ).first() is not None

    devices = session.exec(
        select(DeviceInfo)
        .where(DeviceInfo.customer_id == customer_id)
    ).all()

    for device in devices:
        # do not auto-touch archived devices
        if device.status_id not in (active_status_id, inactive_status_id):
            continue

        new_status = (
            active_status_id if has_active_bill else inactive_status_id
        )

        # update only if status actually changes
        if device.status_id != new_status:
            device.status_id = new_status
            session.add(device)
