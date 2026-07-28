from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

def _create_engine():
    database_url = settings.DATABASE_URL
    if database_url.startswith("sqlite"):
        return create_engine(database_url, connect_args={"check_same_thread": False})

    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect():
            return engine
    except Exception:
        fallback_path = Path(__file__).resolve().parents[2] / "demo.db"
        return create_engine(f"sqlite:///{fallback_path}", connect_args={"check_same_thread": False})


engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def initialize_database() -> None:
    from app.models import claim, customer, policy, user  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    # standard FastAPI pattern - one session per request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
