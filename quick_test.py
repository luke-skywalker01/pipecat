#
# Quick Test - Schneller API Test ohne komplette Pipeline
#

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def quick_api_test():
    """Schneller Test aller APIs ohne Pipeline Setup"""
    print("Quick API Test")
    print("=" * 40)

    # OpenAI Test
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Sage Hallo"}],
            max_tokens=5
        )
        print("OK OpenAI: API verbunden")
    except Exception as e:
        print(f"FEHLER OpenAI: {e}")

    # Deepgram Test
    try:
        from deepgram import DeepgramClient
        client = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
        print("OK Deepgram: API verbunden")
    except Exception as e:
        print(f"FEHLER Deepgram: {e}")

    # ElevenLabs Test
    try:
        import elevenlabs
        client = elevenlabs.client.ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        voices = client.voices.get_all()
        print(f"OK ElevenLabs: API verbunden ({len(voices.voices)} Stimmen)")
    except Exception as e:
        print(f"FEHLER ElevenLabs: {e}")

    # Twilio Test
    try:
        from twilio.rest import Client as TwilioClient
        client = TwilioClient(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        account = client.api.accounts(os.getenv("TWILIO_ACCOUNT_SID")).fetch()
        print(f"OK Twilio: API verbunden ({account.friendly_name})")
    except Exception as e:
        print(f"FEHLER Twilio: {e}")

    print("\nTest abgeschlossen!")

if __name__ == "__main__":
    asyncio.run(quick_api_test())