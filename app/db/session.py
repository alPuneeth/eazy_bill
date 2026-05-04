from sqlmodel import Session, create_engine
from app.core.config import settings

DATABASE_URL = settings.database_url

engine = create_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300
)


def get_session():
    with Session(engine) as session:
        yield session