#!/bin/sh

sleep 10

# echok "DATABASE_NAME=${DATABASE_NAME}\nDATABASE_USER=${DATABASE_USER}\nDATABASE_HOST=${DATABASE_HOST}\nDATABASE_PORT=${DATABASE_PORT}\nDATABASE_PASSWORD=${DATABASE_PASSWORD}\nDATABASE_ROOT_PASSWORD=${DABASE_ROOT_PASSWORD}" > .env

alembic revision --autogenerate -m "Initial migration"

alembic upgrade head

export PYTHONPATH="${PYTHONPATH}:/app"

python default_template/load.py

exec uvicorn main:app --host 0.0.0.0 --port 8000
