#!/usr/bin/env sh
set -euo pipefail

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
    if [ "$i" -ge 180 ]; then
      echo "❌ DB not reachable after 180s" >&2
      exit 1
    fi
    sleep 1
  done
  echo "✅ PostgreSQL is available!"
fi

# ✅ Run migrations only if MIGRATE_ON_START=true
if [ "${MIGRATE_ON_START:-false}" = "true" ]; then
  echo "📦 Running migrations..."
  python manage.py migrate --noinput || {
    echo "❌ Migrations failed" >&2
    exit 1
  }
fi

# Collect static (default true)
if [ "${COLLECTSTATIC:-true}" = "true" ]; then
  echo "🧹 Collecting static files..."
  python manage.py collectstatic --noinput --clear --verbosity=0
fi

echo "🚀 Starting CMD: $*"
exec "$@"
