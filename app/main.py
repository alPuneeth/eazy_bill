from fastapi import FastAPI
from app.core.config import settings
from app.db.database import engine
from sqlalchemy import text


app = FastAPI(title=settings.app_name)


@app.get("/")
def home():
    return {
        "status": "OK",
        "app": settings.app_name,
        "debug": settings.debug
        }


@app.get("/db_check")
def db_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}