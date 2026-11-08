"""Pytest configuration and fixtures."""
import pytest
import asyncio
import os
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import Base, get_db_session, get_session_factory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


# Override settings for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Create engine for in-memory database at module level (before tests are collected)
_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    echo=False,
)
# Import models to register them
from app.models import job, user  # noqa: F401
Base.metadata.create_all(bind=_test_engine)

# Create test session factory
_test_session_factory = sessionmaker(bind=_test_engine, autocommit=False, autoflush=False, class_=Session)

# Override get_session_factory at module level (before any tests import it)
import app.core.database as db_module
db_module.get_session_factory = lambda: _test_session_factory


@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    """Initialize database tables before running tests."""
    # Override the get_db_session dependency
    def override_get_db_session():
        db = _test_session_factory()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    yield
    
    # Clean up
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def async_client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client
    
    import asyncio
    asyncio.run(client.aclose())
