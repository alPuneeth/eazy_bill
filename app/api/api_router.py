from fastapi import APIRouter
from app.api.router.status import router as status_router
from app.api.router.customer_type import router as customer_type_router
from app.api.router.tv_type import router as tv_type_router
from app.api.router.ftth64 import router as ftth64_router


api_router = APIRouter()

api_router.include_router(status_router)
api_router.include_router(customer_type_router)
api_router.include_router(tv_type_router)
api_router.include_router(ftth64_router)
