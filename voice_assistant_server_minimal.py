#
# Minimaler Voice Assistant Server für Railway Test
#

import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

load_dotenv(override=True)

app = FastAPI(title="KI Voice Assistant - Railway Test", description="Minimal Test Version")


@app.get("/")
async def root():
    """Basis-Endpoint"""
    return {"message": "KI Voice Assistant Server läuft auf Railway!", "status": "ready", "version": "minimal-test"}


@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    return {
        "status": "healthy",
        "message": "Voice Assistant Server läuft",
        "port": os.getenv("PORT", "8000"),
        "host": os.getenv("HOST", "0.0.0.0")
    }


@app.post("/webhook/twilio")
async def twilio_webhook(request: Request):
    """
    Twilio Webhook für eingehende Anrufe
    """
    form_data = await request.form()
    print(f"Twilio Webhook aufgerufen: {dict(form_data)}")

    # Dynamische Domain für Produktion/Development
    domain = os.getenv("SERVER_DOMAIN", "localhost:8000")

    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="de-DE">Hallo! Dies ist ein Test des KI Voice Assistenten. Das System läuft erfolgreich auf Railway.</Say>
    <Hangup/>
</Response>"""

    return Response(
        content=twiml_response,
        media_type="application/xml"
    )


@app.get("/config")
async def get_config():
    """Zeigt die aktuelle Konfiguration"""
    return {
        "server_domain": os.getenv("SERVER_DOMAIN", "localhost:8000"),
        "port": os.getenv("PORT", "8000"),
        "host": os.getenv("HOST", "0.0.0.0"),
        "version": "minimal-test",
        "status": "Railway deployment successful"
    }


if __name__ == "__main__":
    # Server-Konfiguration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    print(f"Starte Minimalen Voice Assistant Server auf {host}:{port}")

    # Server starten
    uvicorn.run(
        "voice_assistant_server_minimal:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )