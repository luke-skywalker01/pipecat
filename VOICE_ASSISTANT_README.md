# KI Voice Assistant für Twilio

Ein professioneller KI-Voice-Assistant, der Anrufe über Twilio entgegennimmt und mit ElevenLabs, Deepgram und OpenAI GPT-4o-mini arbeitet.

## Features

- ✅ **Echtzeit-Spracherkennung** mit Deepgram
- ✅ **Natürliche Sprachsynthese** mit ElevenLabs
- ✅ **Intelligente Konversation** mit OpenAI GPT-4o-mini
- ✅ **Twilio-Integration** für Telefonanrufe
- ✅ **Deutscher Kundenservice** optimiert
- ✅ **WebSocket-basierte Echtzeit-Kommunikation**

## Schnellstart

### 1. Installation

```bash
# Repository klonen (falls noch nicht geschehen)
git clone https://github.com/pipecat-ai/pipecat.git
cd pipecat

# Dependencies installieren
pip install -r voice_assistant_requirements.txt
```

### 2. API Keys konfigurieren

Kopieren Sie `.env.example` zu `.env` und füllen Sie Ihre API Keys aus:

```bash
cp .env.example .env
```

Benötigte API Keys:
- **OpenAI API Key**: https://platform.openai.com/api-keys
- **Deepgram API Key**: https://console.deepgram.com/
- **ElevenLabs API Key**: https://elevenlabs.io/app/settings/api-keys
- **Twilio Account SID & Auth Token**: https://console.twilio.com/

### 3. Server starten

```bash
python voice_assistant_server.py
```

Der Server läuft standardmäßig auf `http://localhost:8000`

### 4. Twilio Telefonnummer konfigurieren

1. **Telefonnummer kaufen**: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming

2. **Webhook konfigurieren**:
   - Gehen Sie zu Ihrer Twilio-Nummer
   - Setzen Sie den Webhook URL auf: `https://IHR_SERVER_DOMAIN/webhook/twilio`
   - Methode: `POST`

3. **Öffentliche Domain** (für Produktion):
   - Nutzen Sie einen Cloud-Service (AWS, Google Cloud, etc.)
   - Oder für Tests: ngrok (`ngrok http 8000`)

## Twilio Setup Details

### Lokale Entwicklung mit ngrok

```bash
# ngrok installieren und starten
ngrok http 8000

# Ihre ngrok URL nutzen (z.B. https://abc123.ngrok.io)
# In .env setzen: SERVER_DOMAIN=abc123.ngrok.io
```

### Twilio Webhook Konfiguration

In der Twilio Console:
1. Wählen Sie Ihre Telefonnummer
2. Webhook URL: `https://IHR_DOMAIN/webhook/twilio`
3. HTTP Method: `POST`
4. Speichern

## API Endpoints

- `GET /` - Basis Status
- `GET /health` - Health Check mit API Key Validierung
- `GET /config` - Aktuelle Konfiguration anzeigen
- `POST /webhook/twilio` - Twilio Webhook für eingehende Anrufe
- `WebSocket /ws/twilio` - WebSocket für Echtzeit-Audio

## Anpassungen

### Voice Assistant Persönlichkeit

In `voice_assistant_bot.py` können Sie den System Prompt anpassen:

```python
messages = [
    {
        "role": "system",
        "content": """Ihr angepasster System Prompt hier...""",
    },
]
```

### Stimmen ändern

**ElevenLabs Stimmen** (in `voice_assistant_bot.py`):
```python
tts = ElevenLabsTTSService(
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel (Standard)
    # Andere Optionen:
    # "pNInz6obpgDQGcFmaJgB"  # Adam
    # "EXAVITQu4vr4xnSDxMaL"  # Bella
)
```

### Sprache ändern

**Deepgram Sprache** (in `voice_assistant_bot.py`):
```python
stt = DeepgramSTTService(
    language="de",  # Deutsch
    # Andere Optionen: "en", "fr", "es", etc.
)
```

## Produktionsbereitschaft

### Empfohlene Cloud-Provider

1. **Railway**: Einfaches Deployment
2. **Heroku**: Kostengünstig für kleinere Projekte
3. **AWS/Google Cloud**: Enterprise-Level
4. **DigitalOcean**: Gutes Preis-Leistungs-Verhältnis

### Sicherheit

- Nutzen Sie HTTPS für alle Webhook URLs
- API Keys niemals in Code committen
- Implementieren Sie Rate Limiting
- Monitoring und Logging aktivieren

### Monitoring

Health Check verfügbar unter `/health`:
```bash
curl https://ihr-domain.com/health
```

## Kosten

**Geschätzte Kosten pro Anruf (5 Minuten)**:
- Deepgram STT: ~$0.02
- ElevenLabs TTS: ~$0.03
- OpenAI GPT-4o-mini: ~$0.01
- Twilio: ~$0.02-0.05 (je nach Land)

**Gesamt: ~$0.08-0.11 pro 5-Minuten-Anruf**

## Troubleshooting

### Häufige Probleme

1. **WebSocket Verbindung fehlgeschlagen**
   - Prüfen Sie SERVER_DOMAIN in .env
   - Stellen Sie sicher, dass der Server öffentlich erreichbar ist

2. **Audio-Qualität schlecht**
   - Überprüfen Sie die Netzwerkverbindung
   - Testen Sie verschiedene ElevenLabs Stimmen

3. **API Errors**
   - Validieren Sie alle API Keys mit `/health`
   - Prüfen Sie Kontingente bei den Services

### Logs

Alle Logs werden in der Konsole ausgegeben. Für Produktion empfehlen wir strukturiertes Logging.

## Support

Bei Fragen können Sie:
- Issues im Pipecat Repository erstellen
- Die Dokumentation der jeweiligen Services konsultieren
- Community-Foren nutzen

## Lizenz

Basiert auf Pipecat (BSD 2-Clause License)