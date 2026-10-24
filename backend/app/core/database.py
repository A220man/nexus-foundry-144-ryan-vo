"""Database session management."""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


def get_engine():
    """Create database engine."""
    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
        pool_pre_ping=True,
        echo=settings.debug,
    )
    return engine


def get_session_factory():
    """Create session factory."""
    engine = get_engine()
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


SessionLocal = get_session_factory()


def init_db() -> None:
    """Initialize database tables."""
    # Import all models to register them
    from app.models import job, user  # noqa: F401
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session context manager."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
