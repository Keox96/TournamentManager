"""
Database infrastructure module.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings


class Database:
    """
    Database connection manager using SQLAlchemy async engine.

    Manages the lifecycle of the engine and session factory.
    Must call connect() before use and disconnect() on shutdown.

    Attributes:
        engine (AsyncEngine | None): The SQLAlchemy async engine.
        session_factory (async_sessionmaker | None): The session factory.
    """

    def __init__(self) -> None:
        """
        Initialize a new init instance.
        """
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        """
        Initialize the async engine and session factory.

        Converts postgresql:// to postgresql+asyncpg:// if needed.

        Raises:
            sqlalchemy.exc.ArgumentError: If the database URL is invalid.
        """
        database_url = settings.DATABASE_URL
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )

        self.engine = create_async_engine(
            database_url,
            echo=settings.APP_ENV == "development",
            pool_size=settings.DB_POOL_MIN,
            max_overflow=settings.DB_POOL_MAX - settings.DB_POOL_MIN,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_pre_ping=True,
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def disconnect(self) -> None:
        """
        Dispose the engine and close all connections.

        Should be called on application shutdown.
        """
        if self.engine:
            await self.engine.dispose()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        """
        Provide a session without automatic transaction management.

        The caller is responsible for commit/rollback.

        Yields:
            AsyncSession: An active SQLAlchemy async session.

        Example:
            async with db.get_session() as session:
                await session.execute(select(User))
                await session.commit()
        """
        if self.session_factory is None:
            raise RuntimeError(
                "Database session factory is not initialized. Call connect() first."
            )
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def get_transaction(self) -> AsyncGenerator[AsyncSession]:
        """
        Provide a session with an ACID transaction.

        Auto-commit on success, rollback on exception.

        Yields:
            AsyncSession: An active session with a running transaction.

        Example:
            async with db.get_transaction() as session:
                session.add(user)
                # Auto-commit à la fin du contexte
        """
        if self.session_factory is None:
            raise RuntimeError(
                "Database session factory is not initialized. Call connect() first."
            )
        async with self.session_factory() as session, session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


db = Database()
