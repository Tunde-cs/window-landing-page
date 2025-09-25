FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=LPageToAdmin.settings

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    netcat-openbsd \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY . .


COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# non-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# single-line healthcheck (no fancy line breaks)
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD ["sh","-c","curl -fsS http://127.0.0.1:8000/health/ || exit 1"]

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "LPageToAdmin.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "--access-logfile", "-", "--error-logfile", "-", "--timeout", "60", "--graceful-timeout", "30"]

