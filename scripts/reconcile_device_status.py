from sqlmodel import Session, select

from app.db.session import engine
from app.models.core_models.customer import Customer
from app.services.device_status import sync_device_status_from_bills
from app.services.status_ids import get_active_inactive_status_ids


def run():
    with Session(engine) as session:
        active_status_id, inactive_status_id = (
            get_active_inactive_status_ids(session)
        )

        customer_ids = session.exec(
            select(Customer.id)
        ).all()

        print(f"Reconciling {len(customer_ids)} customers...")

        for customer_id in customer_ids:
            sync_device_status_from_bills(
                customer_id=customer_id,
                session=session,
                active_status_id=active_status_id,
                inactive_status_id=inactive_status_id,
            )

        session.commit()
        print("✅ Device status reconciliation completed")


if __name__ == "__main__":
    run()
