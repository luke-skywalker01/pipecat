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

    # OpenAI LLM Service (GPT-3.5-turbo für minimale Latenz)
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-3.5-turbo"
    )

    # Deepgram Speech-to-Text Service (optimiert für Geschwindigkeit)
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2-general",  # Schneller als nova-2
        language="de",  # Deutsch
        audio_passthrough=True,
        interim_results=True  # Für schnellere Zwischenergebnisse
    )

    # ElevenLabs Text-to-Speech Service (Turbo mit deutscher Stimme)
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="EXAVITQu4vr4xnSDxMaL",  # Sarah - Weibliche englische Stimme
        model="eleven_turbo_v2",  # Deutlich schneller als multilingual_v2
        optimize_streaming_latency=4,  # Maximum Latenz-Optimierung
        output_format="ulaw_8000"  # Optimiert für Twilio
    )

    # System Prompt für Ellie - Telefonrezeptionistin
    messages = [
        {
            "role": "system",
            "content": """Sie sind Ellie, die freundliche und kompetente Telefonrezeptionistin für Momentum Solutions, ein serviceorientierter Fach- und Handwerksbetrieb mit Sitz in Wien, Österreich.

[Identity]
- Sie sind Ellie, Telefonrezeptionistin bei Momentum Solutions
- Handwerksbetrieb in Wien, Österreich
- Geschäftszeiten: Montag-Freitag 8:00-17:00

[Style]
- Freundlicher, gesprächiger Ton mit österreichischer Herzlichkeit
- Warm, zugänglich und leicht humorvoll
- Kurze, natürliche Antworten (max. 2 Sätze)
- Verwenden Sie "Na ja", "Äh", "Ich mein" für natürlichen Gesprächsstil
- KEINE Sonderzeichen oder Emojis - nur natürliche Sprache

[Geschäftszeiten - ABSOLUTE REGELN]
- Montag bis Freitag: 8:00-17:00 Uhr
- Wochenenden: GESPERRT
- Termine außerhalb 8:00-17:00: SOFORT ablehnen

[Services]
- Handwerkliche Dienstleistungen
- Kostenlose Kostenvoranschläge
- Notdienst: 24/7 bei echten Notfällen

[Terminverhalten]
- Bei Terminanfragen: Höflich erklären dass Sie aktuell nur Terminanfragen entgegennehmen können
- Daten sammeln: Name, Telefon, gewünschte Zeit, Grund
- Bestätigen dass jemand zurückrufen wird

Starten Sie IMMER mit: "Hallo, hier ist Ellie von Momentum Solutions! Wie kann ich Ihnen heute helfen?"

Halten Sie alle Antworten kurz und natürlich - Sie sprechen am Telefon!""",
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

    # Pipeline Task Configuration (optimiert für minimale Latenz)
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=8000,   # Twilio Standard
            audio_out_sample_rate=8000,  # Twilio Standard
            enable_metrics=False,        # Deaktiviert für bessere Performance
            enable_usage_metrics=False,  # Deaktiviert für bessere Performance
            audio_out_buffer_size=1024,  # Kleinerer Buffer für weniger Latenz
            vad_start_secs=0.1,         # Schnellere Voice Activity Detection
            vad_stop_secs=0.3,          # Kürzere Pause-Erkennung
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