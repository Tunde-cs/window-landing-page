#!/bin/bash

# Wait for the database to be ready (optional)
# echo "Waiting for Postgres..."
# while ! nc -z $DB_HOST $DB_PORT; do
#   sleep 1
# done
# echo "PostgreSQL started"

# Apply database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting server..."
exec "$@"
