from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from fastapi.exceptions import RequestValidationError
import logging

from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler
    )
from app.core.config import settings
from app.db.session import engine
from app.api.api_router import api_router


app = FastAPI( debug=settings.debug)  # title=settings.app_name | debug=settings.debug

app.include_router(api_router)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

app.add_exception_handler(
    HTTPException,
    http_exception_handler
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s"
)


# home_page
@app.get("/")
def home():
    return {
        "status": "OK",
        "app": settings.app_name,
        "debug": settings.debug
        }


# DB connection check
@app.get("/db_check")
def db_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}