FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.4.10 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 
ENV UV_LINK_MODE=copy

WORKDIR /app

# Ensure uv creates the virtual environment in the standard location
ENV UV_PROJECT_ENVIRONMENT=/usr/local

# Copy application files
COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --frozen --no-install-project

COPY src /app/src

RUN uv sync --frozen

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
