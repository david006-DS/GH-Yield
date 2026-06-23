FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml uv.lock ./
COPY src/ src/
COPY data/ data/
COPY dashboards/ dashboards/

RUN uv sync --frozen --no-dev

EXPOSE 8000 8501

CMD ["uv", "run", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
