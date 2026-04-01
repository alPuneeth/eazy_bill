# from sqlmodel import Session, select
# from datetime import datetime, time, date
# from sqlalchemy.orm import selectinload

# from app.models.core_models.user import User
# from app.models.bill.bill import Bill
# from app.models.devices.device_info import DeviceInfo
# from app.models.core_models.customer import Customer
# from app.models.lookup.village import Village
# from app.models.lookup.ftth64 import FTTH64
# from app.models.lookup.package import Package
# from app.schemas.reports.bills_query import BillReportRead
# from app.schemas.common import IdValueRead


# def get_bills_with_filters(
#         *,
#         session: Session,
#         current_user: User,

#         from_date: date | None = None,
#         to_date: date | None = None,

#         village_ids: list[int] | None = None,
#         ftth64_id: int | None = None
# ) -> list[BillReportRead]:
#     """
#     Returns bill report rows filtered by optional date range,
#     optional village / ftth64 filters, with RBAC enforced.
#     """
#     from fastapi import HTTPException, status

#     # if current_user.role == "agent" and village_ids:
#     #     restricted_exists = session.exec(
#     #         select(Village.id)
#     #         .where(
#     #             Village.id.in_(village_ids),
#     #             Village.agent_restricted == True
#     #         )
#     #     ).first()

#         # if restricted_exists:
#         #     raise HTTPException(
#         #         status_code=status.HTTP_403_FORBIDDEN,
#         #         detail="Access denied for one or more villages"
#         #     )

#     # ── BASE QUERY ──
#     stmt = (
#         select(Bill, DeviceInfo)
#         .select_from(Bill)
#         .join(Customer, Customer.id == Bill.customer_id)
#         .join(Village, Village.id == Customer.village_id)
#         .join(FTTH64, FTTH64.id == Customer.ftth64_id)
#         .join(DeviceInfo, DeviceInfo.customer_id == Customer.id)
#         .join(Package, Package.id == Bill.package_id)
#         .options(
#             selectinload(Bill.customer).selectinload(Customer.village),
#             selectinload(Bill.customer).selectinload(Customer.ftth64),
#             selectinload(Bill.package),
#             selectinload(Bill.created_by),
#         )
#     )

#     # ── RBAC (MANDATORY) ──
#     # if current_user.role == "agent":
#     #     stmt = stmt.where(Village.agent_restricted == False)

#     # ── Optional date filters (inclusive) ──
#     if from_date:
#         from_dt = datetime.combine(from_date, time.min)
#         stmt = stmt.where(Bill.bill_date >= from_dt)

#     if to_date:
#         to_dt = datetime.combine(to_date, time.max)
#         stmt = stmt.where(Bill.bill_date <= to_dt)


#     # ── VILLAGE FILTER ──
#     if village_ids:
#         stmt = stmt.where(Village.id.in_(village_ids))

#     # ── FTTH64 FILTER ──
#     if ftth64_id:
#         stmt = stmt.where(Customer.ftth64_id == ftth64_id)

#     stmt = stmt.order_by(Bill.bill_date.desc())

#     rows = session.exec(stmt).all()

#     # ── MAPPING (ORM → REPORT SCHEMA) ──
#     return [
#         BillReportRead(
#             public_id=bill.public_id,
#             bill_code=bill.bill_code,
#             bill_date=bill.bill_date,
#             start_date=bill.start_date,
#             end_date=bill.end_date,
#             bill_amount=bill.bill_amount,

#             customer_public_id=bill.customer.public_id,
#             customer_name=bill.customer.name,

#             village_name=bill.customer.village.name,

#             vc_number=device.vc_number,
#             ftth64_name=bill.customer.ftth64.name,

#             package=IdValueRead(
#                 id=bill.package.id,
#                 value=bill.package.name
#             ),

#             created_by=IdValueRead(
#                 id=bill.created_by.id,
#                 value=bill.created_by.name  # or email, per your User model
#             ),

#             created_at=bill.created_at,
#             updated_at=bill.updated_at,
#         )
#         for bill, device in rows
#     ]
