"""
FastAPI application configuration and lifespan management.
"""

from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from src.api.exception_handlers import (
    tournament_manager_exception_handler,
    validation_exception_handler,
)
from src.api.v1.players.players_router import player_router
from src.api.v1.teams.teams_router import team_router
from src.api.v1.tournaments.tournaments_router import tournament_router
from src.config import settings
from src.domain.exceptions import TournamentManagerError
from src.infrastructure.database.session import db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Application lifespan context manager.

    This async context manager is passed to FastAPI as the `lifespan` hook.
    On startup it establishes connections/resources required by the application
    (currently it opens the database connection pool via `db.connect()` and
    initializes the database schema with `init_db()`).
    On shutdown it must cleanly release those resources (closing the pool with
    `db.disconnect()`).

    Args:
        app (FastAPI): The application instance the lifespan is attached to.

    Yields:
        None: Control is yielded back to FastAPI to run the application.

    Notes:
        Ensure the `db` object implements `connect()` and `disconnect()` methods
        (see `database.pool.Database`). Any exceptions raised during startup
        will prevent the application from starting.
    """
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
)
# ─── Middleware ───────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# ─── Exception Handlers ───────────────────────────────────────────────────────
app.add_exception_handler(TournamentManagerError, tournament_manager_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
# ─── API Routes ───────────────────────────────────────────────────────────────
app.include_router(tournament_router, prefix=settings.API_PREFIX)
app.include_router(player_router, prefix=settings.API_PREFIX)
app.include_router(team_router, prefix=settings.API_PREFIX)
