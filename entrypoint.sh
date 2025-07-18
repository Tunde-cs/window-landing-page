#!/bin/bash
set -e

echo "🚀 Starting entrypoint..."

# Optional: Wait for Postgres
if [ "$DB_HOST" ]; then
  echo "⏳ Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
  while ! nc -z $DB_HOST $DB_PORT; do
    sleep 1
  done
  echo "✅ PostgreSQL is available!"
fi

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "🧹 Collecting static files..."
python manage.py collectstatic --noinput --verbosity=0

# Start Gunicorn
echo "🚀 Starting Gunicorn..."
exec "$@"
