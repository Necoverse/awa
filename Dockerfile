FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Uygulama kullanıcısı oluştur
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Uygulamayı çalıştır
CMD ["python", "agent.py"] 