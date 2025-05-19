#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate

mkdir -p /app/staticfiles
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
