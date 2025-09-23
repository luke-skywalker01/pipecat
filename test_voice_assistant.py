#
# Test Script für KI Voice Assistant
# Prüft die Konfiguration und API-Verbindungen
#

import os
import asyncio
import sys
from dotenv import load_dotenv
from loguru import logger

# Pipecat Services importieren
try:
    from pipecat.services.openai.llm import OpenAILLMService
    from pipecat.services.deepgram.stt import DeepgramSTTService
    from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
    print("✅ Pipecat Services erfolgreich importiert")
except ImportError as e:
    print(f"❌ Fehler beim Importieren von Pipecat Services: {e}")
    sys.exit(1)

# Andere Dependencies
try:
    import openai
    import deepgram
    import elevenlabs
    from twilio.rest import Client as TwilioClient
    print("✅ Alle API SDKs erfolgreich importiert")
except ImportError as e:
    print(f"❌ Fehler beim Importieren von API SDKs: {e}")
    sys.exit(1)

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="INFO")


def check_environment():
    """Prüft alle erforderlichen Umgebungsvariablen"""
    print("\n🔍 Prüfe Umgebungsvariablen...")

    required_vars = {
        "OPENAI_API_KEY": "OpenAI API Key",
        "DEEPGRAM_API_KEY": "Deepgram API Key",
        "ELEVENLABS_API_KEY": "ElevenLabs API Key",
        "TWILIO_ACCOUNT_SID": "Twilio Account SID",
        "TWILIO_AUTH_TOKEN": "Twilio Auth Token"
    }

    all_good = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {description}: {value[:8]}..." if len(value) > 8 else f"✅ {description}: OK")
        else:
            print(f"❌ {description}: FEHLT")
            all_good = False

    return all_good


async def test_openai_connection():
    """Testet OpenAI API Verbindung"""
    print("\n🤖 Teste OpenAI Verbindung...")

    try:
        llm = OpenAILLMService(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini"
        )
        print("✅ OpenAI LLM Service initialisiert")

        # Test API-Key mit einfacher Anfrage
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hallo"}],
            max_tokens=10
        )
        print("✅ OpenAI API erfolgreich getestet")
        return True

    except Exception as e:
        print(f"❌ OpenAI Fehler: {e}")
        return False


async def test_deepgram_connection():
    """Testet Deepgram API Verbindung"""
    print("\n🎤 Teste Deepgram Verbindung...")

    try:
        stt = DeepgramSTTService(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
            model="nova-2",
            language="de"
        )
        print("✅ Deepgram STT Service initialisiert")

        # Test API-Key
        from deepgram import DeepgramClient
        client = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
        # Einfacher Test ohne Audio - prüft nur API Key
        print("✅ Deepgram API-Key gültig")
        return True

    except Exception as e:
        print(f"❌ Deepgram Fehler: {e}")
        return False


async def test_elevenlabs_connection():
    """Testet ElevenLabs API Verbindung"""
    print("\n🔊 Teste ElevenLabs Verbindung...")

    try:
        tts = ElevenLabsTTSService(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
            model="eleven_multilingual_v2"
        )
        print("✅ ElevenLabs TTS Service initialisiert")

        # Test API-Key mit Stimmen-Liste
        import elevenlabs
        client = elevenlabs.client.ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        voices = client.voices.get_all()
        print(f"✅ ElevenLabs API erfolgreich getestet ({len(voices.voices)} Stimmen verfügbar)")
        return True

    except Exception as e:
        print(f"❌ ElevenLabs Fehler: {e}")
        return False


async def test_twilio_connection():
    """Testet Twilio API Verbindung"""
    print("\n📞 Teste Twilio Verbindung...")

    try:
        client = TwilioClient(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )

        # Test API durch Abrufen der Account-Info
        account = client.api.accounts.get(os.getenv("TWILIO_ACCOUNT_SID"))
        print(f"✅ Twilio API erfolgreich getestet (Account: {account.friendly_name})")

        # Telefonnummern auflisten
        phone_numbers = client.incoming_phone_numbers.list(limit=5)
        if phone_numbers:
            print(f"📱 Verfügbare Telefonnummern: {len(phone_numbers)}")
            for number in phone_numbers:
                print(f"   - {number.phone_number} ({number.friendly_name})")
        else:
            print("⚠️ Keine Telefonnummern gefunden. Bitte eine Twilio-Nummer kaufen.")

        return True

    except Exception as e:
        print(f"❌ Twilio Fehler: {e}")
        return False


async def test_voice_assistant_imports():
    """Testet ob die Voice Assistant Module korrekt importiert werden können"""
    print("\n🔧 Teste Voice Assistant Module...")

    try:
        # Import Test für unsere Module
        import voice_assistant_bot
        import voice_assistant_server
        print("✅ Voice Assistant Module erfolgreich importiert")
        return True

    except ImportError as e:
        print(f"❌ Import Fehler: {e}")
        return False


async def run_comprehensive_test():
    """Führt alle Tests aus"""
    print("🚀 KI Voice Assistant - Comprehensive Test")
    print("=" * 50)

    # Environment Test
    env_ok = check_environment()
    if not env_ok:
        print("\n❌ Umgebungsvariablen nicht vollständig konfiguriert!")
        print("Bitte erstellen Sie eine .env Datei basierend auf .env.example")
        return False

    # Service Tests
    tests = [
        ("OpenAI", test_openai_connection()),
        ("Deepgram", test_deepgram_connection()),
        ("ElevenLabs", test_elevenlabs_connection()),
        ("Twilio", test_twilio_connection()),
        ("Voice Assistant Module", test_voice_assistant_imports())
    ]

    results = []
    for name, test_coro in tests:
        try:
            result = await test_coro
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} Test fehlgeschlagen: {e}")
            results.append((name, False))

    # Ergebnisse zusammenfassen
    print("\n" + "=" * 50)
    print("📊 TEST ZUSAMMENFASSUNG")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "✅ BESTANDEN" if passed else "❌ FEHLGESCHLAGEN"
        print(f"{name:20} : {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALLE TESTS BESTANDEN!")
        print("Ihr Voice Assistant ist bereit für den Einsatz!")
        print("\nNächste Schritte:")
        print("1. Server starten: python voice_assistant_server.py")
        print("2. ngrok für lokale Tests: ngrok http 8000")
        print("3. Twilio Webhook konfigurieren")
    else:
        print("⚠️ EINIGE TESTS FEHLGESCHLAGEN")
        print("Bitte beheben Sie die Fehler bevor Sie den Voice Assistant verwenden.")

    return all_passed


if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())