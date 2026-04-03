FROM python:3.13-slim
LABEL maintainer="TournamentManager"
LABEL description="API REST TournamentManager"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /tm_app

COPY pyproject.toml uv.lock ./

# Crée le venv explicitement puis installe dedans
RUN uv venv /tm_app/.venv --python 3.13
RUN uv sync --frozen --no-dev --no-cache

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /tm_app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uv", "run", "uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]