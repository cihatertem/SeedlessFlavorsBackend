# BASE
FROM python:3.11-bookworm AS base

LABEL maintainer="Cihat Ertem <cihatertem@gmail.com>"

ENV PYTHONUNBUFFERED=1

RUN groupadd -r fastapi && useradd --no-log-init -r -g fastapi fastapi

COPY requirements.txt /tmp/

RUN pip install --upgrade --no-cache-dir pip \
    && pip install --upgrade --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

ENV PATH="/venv/bin:$PATH"

COPY ./app /app

# Dev stage
FROM base AS dev

COPY requirements_dev.txt /tmp/

RUN pip install --upgrade --no-cache-dir -r /tmp/requirements_dev.txt \
    && rm /tmp/requirements_dev.txt

RUN chown -R fastapi:fastapi /app

USER fastapi

WORKDIR /app

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# Prod stage
FROM base as prod

RUN chown -R fastapi:fastapi /app

USER fastapi

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
