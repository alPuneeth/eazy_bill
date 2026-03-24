from fastapi import APIRouter
from app.api.router.status import router as status_router
from app.api.router.customer_type import router as customer_type_router
from app.api.router.tv_type import router as tv_type_router
from app.api.router.ftth64 import router as ftth64_router
from app.api.router.village import router as village_router
from app.api.router.customer_onboard import router as customer_onboard_router
from app.api.router.device_info import router as device_info_router
from app.api.router.package import router as package_router
from app.api.router.user import router as user_router
from app.api.router.bill import router as bill_router
from app.api.router.auth import router as auth_router
from app.api.router.reports.reports_1_2 import router as reports_1_2_router
from app.api.router.reports.report_3 import router as report_3_router
from app.api.router.reports.report_4_collections import router as report_4_router
from app.api.router.reports.report_5_agent_bills import router as report_5_router
from app.api.router.agent_router import router as agent_router


api_router = APIRouter()

api_router.include_router(status_router)
api_router.include_router(customer_type_router)
api_router.include_router(tv_type_router)
api_router.include_router(ftth64_router)
api_router.include_router(village_router)
api_router.include_router(customer_onboard_router)
api_router.include_router(device_info_router)
api_router.include_router(package_router)
api_router.include_router(user_router)
api_router.include_router(bill_router)
api_router.include_router(auth_router)
api_router.include_router(reports_1_2_router)
api_router.include_router(report_3_router)
api_router.include_router(report_4_router)
api_router.include_router(report_5_router)
api_router.include_router(agent_router)
