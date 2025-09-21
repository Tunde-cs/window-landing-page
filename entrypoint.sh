#!/usr/bin/env sh
set -e

echo "🚀 entrypoint starting..."

# Normalize envs (match ECS secrets)
DATABASE_HOST="${DATABASE_HOST:-}"
DATABASE_PORT="${DATABASE_PORT:-5432}"

# Optional: wait for Postgres (max 180s)
if [ -n "$DATABASE_HOST" ]; then
  echo "⏳ Waiting for PostgreSQL at ${DATABASE_HOST}:${DATABASE_PORT} ..."
  i=0
  until nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
    i=$((i+1))
    [ "$i" -ge 180 ] && echo "❌ DB not reachable after 180s" >&2 && exit 1
    sleep 1
  done
  echo "✅ PostgreSQL is available!"
fi

# Optional: only run on web if you really want to (prefer one-off task)
if [ "${MIGRATE_ON_START:-false}" = "true" ]; then
  echo "📦 Running migrations..."
  python manage.py migrate --noinput
fi

# Collect static (safe with Whitenoise)
if [ "${COLLECTSTATIC:-true}" = "true" ]; then
  echo "🧹 Collecting static files..."
  python manage.py collectstatic --noinput --verbosity=0
fi

echo "🚀 Starting: $*"
exec "$@"
