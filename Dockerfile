FROM python:11-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY app/pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python.3.11-slim-bookworm

WORKDIR  /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
