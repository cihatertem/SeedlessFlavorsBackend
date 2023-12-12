# Dev stage
FROM python:3.11-bookworm AS dev

LABEL maintainer="Cihat Ertem <cihatertem@gmail.com>"

ENV PYTHONUNBUFFERED=1

RUN groupadd -r fastapi && useradd --no-log-init -r -g fastapi fastapi

WORKDIR /app

COPY requirements.txt requirements.dev.txt /tmp/

RUN pip install --upgrade --no-cache-dir pip \
    && pip install --upgrade --no-cache-dir -r /tmp/requirements.txt -r /tmp/requirements.dev.txt \
    && rm /tmp/requirements*.txt

COPY ./app .

RUN chown -R fastapi:fastapi /app

USER fastapi

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]

# Prod stage
FROM python:3.11.0-bookworm as prod

COPY --from=dev /app /app

USER fastapi

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "2"]

# Test stage
FROM dev as test

ENV PATH="/app:/tests:$PATH"

COPY tests /tests

COPY pytest.ini /

WORKDIR /

USER root

CMD ["pytest"]