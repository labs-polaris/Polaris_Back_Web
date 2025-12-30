#!/bin/sh
set -e

export PYTHONPATH=/app

echo "Waiting for database..."
python /app/docker/wait_for_db.py

echo "Running migrations..."
alembic upgrade head

echo "Ensuring tables exist..."
python /app/docker/ensure_tables.py

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
