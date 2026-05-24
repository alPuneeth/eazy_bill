
# -------------------- LOGGING --------------------

import logging
from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse
from sqlmodel import Session

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

# -------------------- IMPORTS --------------------

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlmodel import select
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler
    )
from app.core.config import settings
from app.db.session import get_session
from app.api.api_router import api_router


# -------------------- LIFESPAN (REPLACES on_event) --------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started")
    yield
    logger.info("Application shutdown")


# -------------------- APP INIT --------------------
tags_metadata = [
    {"name": "Health"},
    {"name": "Auth"},
    {"name": "User"},
    {"name": "Agent"},
    {"name": "Village"},
    {"name": "Package"},
    {"name": "Status"},
    {"name": "CustomerType"},
    {"name": "FTTH64"},
    {"name": "TVType"},
    {"name": "Customer"},
    {"name": "DeviceInfo"},
    {"name": "Bill"},
    {"name": "Reports"},

]


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=tags_metadata
    ) 

app.include_router(api_router)


# -------------------- EXCEPTION HANDLERS --------------------
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler  # type: ignore
)

app.add_exception_handler(
    HTTPException,
    http_exception_handler   # type: ignore
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"{request.method} {request.url} failed")

    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"}
    )

# -------------------- ROOT --------------------

@app.get("/", tags=["Health"])
def home():
    return {
        "status": "OK",
        "app": settings.app_name,
        "debug": settings.debug
        }


# -------------------- DB CHECK --------------------

@app.get("/db_check", tags=["Health"])
def db_check(db: Session = Depends(get_session)):
    try:
        db.exec(select(1))

        logger.info("DB connection successful")
        return {"database": "connected"}

    except Exception:
        logger.exception("DB connection failed")

        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )
    