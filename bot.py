#!/usr/bin/env python3

"""
Railway Twilio Voice Assistant
Real implementation with pipecat integration
"""

import os
import asyncio
from fastapi import FastAPI
from fastapi.websockets import WebSocket
import uvicorn
from dotenv import load_dotenv
from loguru import logger

# Import the official pipecat voice assistant
from voice_assistant_official import bot as voice_bot, run_bot
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport

load_dotenv(override=True)

app = FastAPI(title="Pipecat Twilio Voice Assistant")

# Transport configuration from voice_assistant_official.py
transport_params = {
    "twilio": lambda: FastAPIWebsocketParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
        turn_analyzer=LocalSmartTurnAnalyzerV3(params=SmartTurnParams()),
    ),
}

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
    """Twilio webhook endpoint - starts voice assistant session"""
    logger.info("Twilio webhook called - voice assistant session starting")
    return {
        "status": "webhook_received",
        "message": "Voice assistant webhook is ready"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for Twilio Media Streams"""
    await websocket.accept()
    logger.info("WebSocket connection accepted for Twilio")

    try:
        # Create runner arguments for Twilio transport
        runner_args = RunnerArguments(
            transport="twilio",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            handle_sigint=False,
            pipeline_idle_timeout_secs=30
        )

        # Run the voice assistant
        await voice_bot(runner_args)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting Pipecat Twilio Voice Assistant on {host}:{port}")
    logger.info("Available endpoints:")
    logger.info("  GET  / - Root endpoint")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /webhook/twilio - Twilio webhook")
    logger.info("  WS   /ws - WebSocket for Twilio streams")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )