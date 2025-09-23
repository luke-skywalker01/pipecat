#
# FastAPI Server für KI Voice Assistant mit Twilio Integration
#

import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from loguru import logger
from voice_assistant_bot import handle_twilio_call

load_dotenv(override=True)

app = FastAPI(title="KI Voice Assistant", description="Twilio Voice Assistant mit ElevenLabs, Deepgram und OpenAI")


@app.get("/")
async def root():
    """Basis-Endpoint"""
    return {"message": "KI Voice Assistant Server läuft", "status": "ready"}


@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    required_vars = ["OPENAI_API_KEY", "DEEPGRAM_API_KEY", "ELEVENLABS_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "missing_env_vars": missing_vars}
        )

    return {"status": "healthy", "message": "Alle API Keys konfiguriert"}


@app.post("/webhook/twilio")
async def twilio_webhook():
    """
    Twilio Webhook für eingehende Anrufe
    Dieser Endpoint wird von Twilio aufgerufen, wenn ein Anruf eingeht
    """
    # TwiML Response für Twilio
    # Dynamische Domain für Produktion/Development
    domain = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('SERVER_DOMAIN', 'localhost:8000')

    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="de-DE">Verbinde Sie mit unserem KI Assistenten. Bitte warten Sie einen Moment.</Say>
    <Connect>
        <Stream url="wss://{domain}/ws/twilio" />
    </Connect>
</Response>"""

    from fastapi.responses import Response
    return Response(
        content=twiml_response,
        media_type="application/xml"
    )


@app.websocket("/ws/twilio")
async def twilio_websocket(websocket: WebSocket):
    """
    WebSocket Endpoint für Twilio Media Streams
    Hier wird die Echtzeit-Audiokommunikation abgewickelt
    """
    await websocket.accept()
    logger.info("Twilio WebSocket Verbindung akzeptiert")

    try:
        await handle_twilio_call(websocket)
    except WebSocketDisconnect:
        logger.info("Twilio WebSocket Verbindung beendet")
    except Exception as e:
        logger.error(f"Fehler in Twilio WebSocket: {e}")
    finally:
        logger.info("Twilio WebSocket Handler beendet")


@app.get("/config")
async def get_config():
    """Zeigt die aktuelle Konfiguration (ohne API Keys)"""
    return {
        "twilio_account_sid": os.getenv("TWILIO_ACCOUNT_SID", "Nicht konfiguriert")[:8] + "..." if os.getenv("TWILIO_ACCOUNT_SID") else "Nicht konfiguriert",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "deepgram_configured": bool(os.getenv("DEEPGRAM_API_KEY")),
        "elevenlabs_configured": bool(os.getenv("ELEVENLABS_API_KEY")),
        "server_domain": os.getenv("SERVER_DOMAIN", "localhost:8000")
    }


if __name__ == "__main__":
    # Server-Konfiguration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    logger.info(f"Starte KI Voice Assistant Server auf {host}:{port}")

    # Server starten
    uvicorn.run(
        "voice_assistant_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )