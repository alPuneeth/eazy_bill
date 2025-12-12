from sqlmodel import Session, create_engine
from app.core.config import settings

DATABASE_URL = settings.database_url

engine = create_engine(
    DATABASE_URL,
    echo=settings.debug
)


def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()