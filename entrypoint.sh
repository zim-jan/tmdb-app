#!/usr/bin/env bash
set -e

# Apply database migrations
python manage.py migrate --noinput

# Start server
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${GUNICORN_WORKERS:-3}
