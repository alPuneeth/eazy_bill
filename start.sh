#!/bin/bash

set -e

export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+psycopg://}"
export TEST_DATABASE_URL="${TEST_DATABASE_URL/postgresql:\/\//postgresql+psycopg://}"

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000