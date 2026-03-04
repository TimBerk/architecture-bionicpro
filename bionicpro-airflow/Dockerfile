FROM apache/airflow:3.1.7

USER root
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /opt/airflow
COPY pyproject.toml uv.lock ./

ENV UV_PROJECT_ENVIRONMENT=/usr/local
ENV UV_SYSTEM_PYTHON=1
ENV UV_COMPILE_BYTECODE=1

RUN uv sync --no-install-project --frozen

ENV PATH=/opt/airflow/.local/bin:$PATH

USER airflow
