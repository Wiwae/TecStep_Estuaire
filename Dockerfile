FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY /pyproject.toml .
COPY /uv.lock .
COPY 01_model_deployment /inference_service
WORKDIR /inference_service/app
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]