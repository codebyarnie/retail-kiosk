"""Shared pytest fixtures for backend tests.

This module provides common fixtures for database sessions, test clients,
and sample data that can be used across all test modules.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.dependencies.database import get_db
from app.main import app
from app.models import Base

# Use SQLite in-memory for tests - lightweight and isolated
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create a session-scoped event loop.

    This allows async fixtures and tests to use the same event loop
    throughout the test session, which is required for session-scoped
    async fixtures.

    Yields:
        asyncio.AbstractEventLoop: The event loop for the test session
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """Create a function-scoped async engine with fresh tables.

    Creates and drops all tables for each test to ensure isolation.

    Yields:
        AsyncEngine: The SQLAlchemy async engine for tests
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # Enable SQLite foreign key support
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a function-scoped async session for database operations.

    This fixture provides an isolated database session for each test,
    ensuring that tests don't interfere with each other.

    Args:
        db_engine: The async database engine fixture

    Yields:
        AsyncSession: An async database session for the test
    """
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP test client with database dependency override.

    This fixture overrides the database dependency to use the test session,
    allowing API tests to use the isolated test database.

    Args:
        db_session: The async database session fixture

    Yields:
        AsyncClient: An httpx AsyncClient configured for testing
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        """Override the get_db dependency to use the test session."""
        yield db_session

    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_product_data() -> dict[str, Any]:
    """Provide sample product data for tests.

    Returns:
        dict: A dictionary containing sample product attributes
    """
    return {
        "sku": "TEST-001",
        "name": "Test Product",
        "description": "A test product for unit testing",
        "short_description": "Test product",
        "price": 19.99,
        "image_url": "https://example.com/images/test-product.jpg",
        "thumbnail_url": "https://example.com/images/test-product-thumb.jpg",
        "attributes": {"material": "steel", "size": "M"},
        "specifications": {"weight": "100g", "dimensions": "10x5x3cm"},
        "is_active": True,
        "is_featured": False,
    }


@pytest.fixture
def sample_category_data() -> dict[str, Any]:
    """Provide sample category data for tests.

    Returns:
        dict: A dictionary containing sample category attributes
    """
    return {
        "name": "Test Category",
        "slug": "test-category",
        "description": "A test category for unit testing",
        "image_url": "https://example.com/images/test-category.jpg",
        "display_order": 1,
        "is_active": True,
        "parent_id": None,
    }


@pytest.fixture
def sample_session_data() -> dict[str, Any]:
    """Provide sample user session data for tests.

    Returns:
        dict: A dictionary containing sample session attributes
    """
    return {
        "session_id": "test-session-12345678",
        "device_type": "kiosk",
        "user_agent": "TestBrowser/1.0",
        "ip_address": "192.168.1.100",
    }


@pytest.fixture
def sample_list_data() -> dict[str, Any]:
    """Provide sample user list data for tests.

    Returns:
        dict: A dictionary containing sample list attributes
    """
    return {
        "list_id": "list-12345678",
        "name": "My Shopping List",
        "description": "Items for the weekend project",
        "share_code": None,
    }


@pytest.fixture
def sample_analytics_event_data() -> dict[str, Any]:
    """Provide sample analytics event data for tests.

    Returns:
        dict: A dictionary containing sample analytics event attributes
    """
    return {
        "event_type": "view_product",
        "event_data": {"sku": "TEST-001", "source": "search"},
        "product_sku": "TEST-001",
        "search_query": None,
    }


# ============================================================================
# Mock Fixtures for External Services
# ============================================================================


@pytest.fixture
def mock_qdrant_client() -> MagicMock:
    """Create a mock Qdrant client for vector search tests.

    Returns:
        MagicMock: A mocked Qdrant client
    """
    mock = MagicMock()
    mock.search = AsyncMock(return_value=[])
    mock.upsert = AsyncMock(return_value=None)
    mock.delete = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_embedding_service() -> MagicMock:
    """Create a mock embedding service for tests.

    Returns:
        MagicMock: A mocked embedding service
    """
    mock = MagicMock()
    mock.generate_embedding = MagicMock(return_value=[0.1] * 384)
    mock.batch_embeddings = MagicMock(return_value=[[0.1] * 384, [0.2] * 384])
    return mock


@pytest.fixture
def mock_redis_client() -> MagicMock:
    """Create a mock Redis client for caching tests.

    Returns:
        MagicMock: A mocked Redis client
    """
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.exists = AsyncMock(return_value=0)
    return mock
