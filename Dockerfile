FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=LPageToAdmin.settings

WORKDIR /app

# OS deps (only what you need)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libpq-dev postgresql-client netcat-openbsd curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Python deps first (better caching)
COPY requirements.txt .
RUN pip install --upgrade pip==24.2 setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user BEFORE copying code
RUN useradd -m -u 1000 appuser

# Copy app code owned by appuser; prepare static dir
COPY --chown=appuser:appuser . /app
RUN mkdir -p /app/staticfiles

# Collect static files at build time (ignore errors if settings need DB)
RUN python manage.py collectstatic --noinput || true

# Entrypoint
COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Drop privileges
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD ["sh","-c","curl -fsS http://127.0.0.1:8000/health/ || exit 1"]

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn","LPageToAdmin.wsgi:application", \
     "--bind","0.0.0.0:8000", \
     "--workers","3", \
     "--threads","2", \
     "--max-requests","500", \
     "--max-requests-jitter","50", \
     "--access-logfile","-", \
     "--error-logfile","-", \
     "--timeout","60", \
     "--graceful-timeout","30"]
