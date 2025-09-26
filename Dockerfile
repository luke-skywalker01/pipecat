# Railway Minimal Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Minimal system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only essential files
COPY requirements.txt .
COPY voice_assistant_server_minimal.py voice_assistant_server.py

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Environment
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

CMD ["python", "voice_assistant_server.py"]
