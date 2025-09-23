#
# KI Voice Assistant für Kundenanrufe mit Twilio
# Nutzt ElevenLabs TTS, Deepgram STT und OpenAI GPT-4o-mini
#

import os
import sys
import json
from dotenv import load_dotenv
from fastapi import WebSocket
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


async def run_voice_assistant(websocket_client: WebSocket, stream_sid: str, call_sid: str):
    """
    Hauptfunktion für den KI Voice Assistant
    """
    # Twilio Serializer Setup
    serializer = TwilioFrameSerializer(
        stream_sid=stream_sid,
        call_sid=call_sid,
        account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
        auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
    )

    # WebSocket Transport für Twilio
    transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            vad_analyzer=SileroVADAnalyzer(),
            serializer=serializer,
        ),
    )

    # OpenAI LLM Service (GPT-4o-mini)
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )

    # Deepgram Speech-to-Text Service
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2",
        language="de",  # Deutsch
        audio_passthrough=True
    )

    # ElevenLabs Text-to-Speech Service
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="Rc6mVxOkevStnSH2pUO9",  # Ihre gewählte Stimme
        model="eleven_multilingual_v2"
    )

    # System Prompt für Kundenservice
    messages = [
        {
            "role": "system",
            "content": """Du bist ein professioneller KI-Kundenberater. Du hilfst Kunden bei ihren Anfragen höflich und kompetent.

Wichtige Regeln:
- Antworte immer auf Deutsch
- Sei höflich und professionell
- Halte deine Antworten kurz und präzise (max. 2-3 Sätze)
- Verwende keine Sonderzeichen, da deine Antwort in Sprache umgewandelt wird
- Bei komplexen Problemen biete an, einen menschlichen Mitarbeiter zu verbinden
- Frage nach der Kundennummer, wenn nötig
- Dokumentiere wichtige Informationen

Du kannst bei folgenden Themen helfen:
- Allgemeine Produktinformationen
- Bestellstatus
- Rechnungsfragen
- Technischer Support Level 1
- Terminvereinbarungen

Starte das Gespräch mit einer freundlichen Begrüßung.""",
        },
    ]

    # LLM Context Setup
    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    # Pipeline Setup
    pipeline = Pipeline(
        [
            transport.input(),           # Twilio Audio Input
            stt,                        # Deepgram Speech-to-Text
            context_aggregator.user(),  # User Context
            llm,                        # OpenAI LLM
            tts,                        # ElevenLabs Text-to-Speech
            transport.output(),         # Twilio Audio Output
            context_aggregator.assistant(),  # Assistant Context
        ]
    )

    # Pipeline Task Configuration
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=8000,   # Twilio Standard
            audio_out_sample_rate=8000,  # Twilio Standard
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        """Wird ausgeführt, wenn ein Anruf eingeht"""
        logger.info(f"Neuer Anruf verbunden: {call_sid}")

        # Begrüßung starten
        greeting_message = {
            "role": "system",
            "content": "Begrüße den Kunden freundlich und frage, wie du helfen kannst."
        }
        messages.append(greeting_message)
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        """Wird ausgeführt, wenn der Anruf beendet wird"""
        logger.info(f"Anruf beendet: {call_sid}")
        await task.cancel()

    # Pipeline Runner starten
    runner = PipelineRunner(handle_sigint=False, force_gc=True)
    await runner.run(task)


async def handle_twilio_call(websocket: WebSocket):
    """
    Handler für eingehende Twilio WebSocket Verbindungen
    """
    logger.info("Neue Twilio WebSocket Verbindung")

    # Erste beiden Nachrichten von Twilio lesen
    start_data = websocket.iter_text()
    await start_data.__anext__()  # Erste Nachricht überspringen

    # Zweite Nachricht enthält Call-Details
    call_data = json.loads(await start_data.__anext__())

    # Stream- und Call-IDs extrahieren
    stream_sid = call_data["start"]["streamSid"]
    call_sid = call_data["start"]["callSid"]

    logger.info(f"Twilio Call Details - CallSid: {call_sid}, StreamSid: {stream_sid}")

    # Voice Assistant starten
    await run_voice_assistant(websocket, stream_sid, call_sid)