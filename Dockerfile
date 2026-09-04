# Production container for InsForge Compute (FastAPI / Uvicorn).
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY alembic ./alembic
COPY alembic.ini ./

RUN useradd --create-home --uid 10001 appuser \
    && chown --recursive appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn agent_ready_merchant.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
