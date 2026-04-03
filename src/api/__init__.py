from .app import app

from config import settings


@app.get("/", tags=["Info"])
def root():
    return {"app": settings.APP_NAME, "docs": "/docs"}


@app.get(f"{settings.API_PREFIX}/health", tags=["Info"])
def health():
    return {"status": "ok", "service": settings.APP_NAME}
