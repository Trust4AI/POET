FROM python:3.11 as builder

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false

RUN poetry install --no-root --no-dev

WORKDIR /app

COPY ./src /app

COPY ./docker/shell /app/shell

RUN chmod +x /app/shell/entrypoint.sh

CMD ["/app/shell/entrypoint.sh"]
