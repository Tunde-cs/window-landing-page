# ----------------------------------------------------------
# 📦 Base Image
# ----------------------------------------------------------
FROM python:3.10-slim

# ----------------------------------------------------------
# 🛠️ Environment Variables
# ----------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ----------------------------------------------------------
# 📁 Set Working Directory
# ----------------------------------------------------------
WORKDIR /app

# ----------------------------------------------------------
# 🧰 Install System Dependencies
# ----------------------------------------------------------
RUN apt-get update && apt-get install -y \
    netcat-openbsd gcc postgresql libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# 📄 Install Python Dependencies
# ----------------------------------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ----------------------------------------------------------
# 📦 Copy Project Files
# ----------------------------------------------------------
COPY . .

# ----------------------------------------------------------
# 🧹 Collect Static Files
# ----------------------------------------------------------
RUN python manage.py collectstatic --noinput

# ----------------------------------------------------------
# 🚦 Healthcheck for ECS / ALB
# ----------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# ----------------------------------------------------------
# 🚪 Expose Port
# ----------------------------------------------------------
EXPOSE 8000

# ----------------------------------------------------------
# 🚀 Start Django Dev Server (for ECS testing)
# ----------------------------------------------------------

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "LPageToAdmin.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3"]

