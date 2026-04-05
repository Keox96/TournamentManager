"""
FastAPI API module.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.session import db


async def get_db_transaction() -> AsyncGenerator[AsyncSession]:
    """
    Dependency that provides an async database session with transaction.

    This dependency yields a database session that has an active transaction.
    The transaction will be committed automatically when the context exits
    successfully, or rolled back if an exception occurs.

    Usage:
        @app.get("/endpoint")
        async def endpoint(session: AsyncSession = Depends(get_db_transaction)):
            # Use session here
            pass
    """
    async with db.get_transaction() as t_session:
        yield t_session


# ── Type aliases réutilisables dans tous les routers ─────────────────────────
DbSession = Annotated[AsyncSession, Depends(get_db_transaction)]
