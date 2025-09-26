# Railway Official Pipecat Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies für Audio Processing
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    ca-certificates \
    libasound2-dev \
    portaudio19-dev \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY bot.py bot.py
COPY .env.example .env

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

# Start the FastAPI server directly
CMD ["python", "bot.py"]
