from fastapi import APIRouter
from app.api.router.status import router as status_router
from app.api.router.customer_type import router as customer_type_router
from app.api.router.tv_type import router as tv_type_router
from app.api.router.ftth64 import router as ftth64_router
from app.api.router.village import router as village_router
from app.api.router.customer import router as customer_router
from app.api.router.device_info import router as device_info_router
from app.api.router.package import router as package_router


api_router = APIRouter()

api_router.include_router(status_router)
api_router.include_router(customer_type_router)
api_router.include_router(tv_type_router)
api_router.include_router(ftth64_router)
api_router.include_router(village_router)
api_router.include_router(customer_router)
api_router.include_router(device_info_router)
api_router.include_router(package_router)
