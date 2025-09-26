#!/usr/bin/env python3

"""
Simple FastAPI Health Server for Railway
This will get the basic deployment working first
"""

import os
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI(title="Pipecat Voice Assistant")

@app.get("/")
async def root():
    return {
        "message": "Pipecat Voice Assistant is running",
        "service": "twilio",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Railway health check endpoint"""
    return {
        "status": "healthy",
        "service": "pipecat-voice-assistant",
        "transport": "twilio",
        "endpoints": ["/", "/health", "/webhook/twilio"]
    }

@app.post("/webhook/twilio")
async def twilio_webhook():
    """Twilio webhook endpoint - placeholder for now"""
    return {
        "status": "webhook_received",
        "message": "Voice assistant webhook is ready"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"Starting Simple FastAPI Server on {host}:{port}")
    print("Available endpoints:")
    print("  GET  / - Root endpoint")
    print("  GET  /health - Health check")
    print("  POST /webhook/twilio - Twilio webhook")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )