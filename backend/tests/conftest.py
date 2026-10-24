"""Pytest configuration and fixtures."""
import pytest
import asyncio
import os
from httpx import AsyncClient
from app.main import app
from app.core.database import init_db, get_engine, Base, get_session_factory
from app.core.config import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from unittest.mock import patch


# Override settings for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    """Initialize database tables before running tests."""
    # Create engine for in-memory database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
        echo=False,
    )
    # Import models
    from app.models import job, user  # noqa: F401
    Base.metadata.create_all(bind=engine)
    
    # Override the app's session factory to use the test engine
    from app.core.database import SessionLocal
    test_session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    import app.core.database as db_module
    db_module.SessionLocal = test_session_factory
    
    # Also override get_session_factory to return the test factory
    db_module.get_session_factory = lambda: test_session_factory
    
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
async def async_client():
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

