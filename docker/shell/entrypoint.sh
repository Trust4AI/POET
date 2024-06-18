#!/bin/sh

sleep 10

mkdir -p /app/alembic/versions

# Generar la migración inicial si no existe
if [ -z "$(ls -A /app/alembic/versions)" ]; then
   echo "Generating initial migration..."
   alembic -c /app/alembic.ini revision --autogenerate -m "Initial migration"
fi

alembic upgrade head


export PYTHONPATH="${PYTHONPATH}:/app"

chmod +x default_template/load.py

exec uvicorn main:app --host 0.0.0.0 --port 8000 &

sleep 5

python default_template/load.py

wait