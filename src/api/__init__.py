from config import settings

from .app import app


@app.get("/", tags=["Info"])
def root() -> dict[str, str]:
    return {"app": settings.APP_NAME, "docs": "/docs"}


@app.get(f"{settings.API_PREFIX}/health", tags=["Info"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.APP_NAME}
