"""Pytest configuration and fixtures for testing."""

from collections.abc import AsyncGenerator

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api.app import app
from src.api.dependencies import get_db_transaction
from src.config import settings
from src.infrastructure.database.models import Base


def _sqlalchemy_database_url(database_url: str) -> str:
    """Convert a PostgreSQL URL to SQLAlchemy asyncpg URL."""
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


def _asyncpg_database_url(database_url: str) -> str:
    """Convert SQLAlchemy asyncpg URL to a plain asyncpg-compatible URL."""
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return database_url


@pytest_asyncio.fixture
async def test_session_factory() -> AsyncGenerator[async_sessionmaker[AsyncSession]]:
    """Create a test database and SQLAlchemy session factory, yield it, then clean up."""
    database_url = _asyncpg_database_url(settings.DATABASE_URL)
    base_url = database_url.rsplit("/", 1)[0]  # Get base URL without DB name
    # Use a separate test database
    test_database_name = "tournament_manager_test"
    test_db_url = base_url + "/" + test_database_name

    # Connect to postgres (system DB) to create/drop the test DB
    postgres_system_url = base_url + "/postgres"
    postgres_conn = await asyncpg.connect(postgres_system_url)

    try:
        # Drop the test database if it exists
        await postgres_conn.execute(f"DROP DATABASE IF EXISTS {test_database_name}")
        # Create the test database
        await postgres_conn.execute(f"CREATE DATABASE {test_database_name}")
    finally:
        await postgres_conn.close()

    # Create SQLAlchemy async engine for the test database.
    test_engine = create_async_engine(
        _sqlalchemy_database_url(test_db_url),
        echo=settings.APP_ENV == "development",
        pool_size=settings.DB_POOL_MIN,
        max_overflow=settings.DB_POOL_MAX - settings.DB_POOL_MIN,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_pre_ping=True,
    )

    test_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    # Initialize schema in test database using SQLAlchemy metadata.
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_session_factory

    await test_engine.dispose()

    # Cleanup: drop test database after closing SQLAlchemy engine.
    postgres_conn = await asyncpg.connect(postgres_system_url)
    try:
        await postgres_conn.execute(f"DROP DATABASE IF EXISTS {test_database_name}")
    finally:
        await postgres_conn.close()


@pytest_asyncio.fixture
async def test_client(
    test_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient]:
    """Provide a test client with overridden database dependency."""

    async def override_get_db_transaction() -> AsyncGenerator[AsyncSession]:
        """Override get_db_transaction to use the test SQLAlchemy session."""
        async with test_session_factory() as session, session.begin():
            yield session

    # Override the dependency
    app.dependency_overrides[get_db_transaction] = override_get_db_transaction

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Clear overrides
    app.dependency_overrides.clear()
