from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine
from app.api.api_router import api_router


app = FastAPI(title=settings.app_name)

app.include_router(api_router)


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