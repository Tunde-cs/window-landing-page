# ----------------------------------------------------------
# 📦 Base Image
# ----------------------------------------------------------
FROM python:3.10-slim

# ----------------------------------------------------------
# 🧾 Metadata
# ----------------------------------------------------------
LABEL maintainer="Tunde <tunde@hotengroup.com>"
LABEL app="WindowGeniusAI"
LABEL stage="production"

# ----------------------------------------------------------
# 🛠️ Environment Variables
# ----------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

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
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------------
# 📦 Copy Project Files
# ----------------------------------------------------------
COPY . .

# ----------------------------------------------------------
# ✅ Copy Entrypoint
# ----------------------------------------------------------
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ----------------------------------------------------------
# 🧪 Healthcheck for ECS / ALB
# ----------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/ || exit 1

# ----------------------------------------------------------
# 🚪 Expose Port
# ----------------------------------------------------------
EXPOSE ${PORT}

# ----------------------------------------------------------
# 🚀 Start App
# ----------------------------------------------------------
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "LPageToAdmin.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3"]
