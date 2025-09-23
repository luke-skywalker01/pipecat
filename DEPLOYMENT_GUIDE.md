# 🚀 Voice Assistant Deployment Guide

Komplette Anleitung für das Deployment des KI Voice Assistants in verschiedenen Cloud-Umgebungen.

## 📋 Übersicht

- [Railway (Empfohlen)](#railway-deployment)
- [Heroku](#heroku-deployment)
- [Google Cloud Run](#google-cloud-run)
- [AWS EC2](#aws-ec2)
- [DigitalOcean](#digitalocean)
- [Azure Container Instances](#azure-container-instances)

---

## 🚄 Railway Deployment (Empfohlen)

Railway ist am einfachsten für Voice Assistant Deployments.

### Setup

1. **Account erstellen**: https://railway.app
2. **GitHub Repository verbinden**
3. **Umgebungsvariablen konfigurieren**

### Konfiguration

```bash
# Railway Project erstellen
npm install -g @railway/cli
railway login
railway init
```

**`railway.json`:**
```json
{
  "name": "voice-assistant",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python voice_assistant_server.py",
    "healthcheckPath": "/health"
  }
}
```

**Environment Variables in Railway:**
```
OPENAI_API_KEY=sk-proj-...
DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
PORT=8000
```

### Deployment

```bash
# Deployment
railway up

# Domain abrufen
railway domain
```

**Kosten**: $5-20/Monat

---

## 🟣 Heroku Deployment

### Setup

1. **Heroku CLI installieren**: https://devcenter.heroku.com/articles/heroku-cli
2. **App erstellen**

```bash
# Login und App erstellen
heroku login
heroku create voice-assistant-app

# Python Buildpack
heroku buildpacks:set heroku/python
```

### Konfiguration

**`Procfile`:**
```
web: python voice_assistant_server.py
```

**`runtime.txt`:**
```
python-3.10.12
```

**Environment Variables:**
```bash
heroku config:set OPENAI_API_KEY=sk-proj-...
heroku config:set DEEPGRAM_API_KEY=...
heroku config:set ELEVENLABS_API_KEY=...
heroku config:set TWILIO_ACCOUNT_SID=AC...
heroku config:set TWILIO_AUTH_TOKEN=...
```

### Deployment

```bash
# Git Setup
git add .
git commit -m "Initial deployment"
git push heroku main

# App öffnen
heroku open
```

**Domain**: `https://voice-assistant-app.herokuapp.com`
**Kosten**: $7-25/Monat

---

## ☁️ Google Cloud Run

### Setup

1. **Google Cloud SDK installieren**
2. **Projekt erstellen**

```bash
# Login
gcloud auth login
gcloud config set project DEIN-PROJECT-ID
```

### Dockerfile

**`Dockerfile`:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Dependencies installieren
COPY voice_assistant_requirements.txt .
RUN pip install --no-cache-dir -r voice_assistant_requirements.txt

# App Code kopieren
COPY voice_assistant_bot.py .
COPY voice_assistant_server.py .

# Port freigeben
EXPOSE 8080

# Server starten
CMD ["python", "voice_assistant_server.py"]
```

**Environment Setup:**
```bash
# .env für Cloud Run
echo "PORT=8080" > .env.production
```

### Deployment

```bash
# Container bauen und deployen
gcloud run deploy voice-assistant \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY,DEEPGRAM_API_KEY=$DEEPGRAM_API_KEY,ELEVENLABS_API_KEY=$ELEVENLABS_API_KEY,TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN
```

**Kosten**: $0-20/Monat (Pay-per-use)

---

## 🟠 AWS EC2

### Setup

1. **EC2 Instance starten** (t3.micro für Tests, t3.small für Produktion)
2. **SSH-Zugang einrichten**

```bash
# Instance verbinden
ssh -i key.pem ubuntu@EC2-IP

# Updates und Python
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx -y
```

### Application Setup

```bash
# App Directory
sudo mkdir /opt/voice-assistant
sudo chown ubuntu:ubuntu /opt/voice-assistant
cd /opt/voice-assistant

# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Code hochladen (via git oder scp)
git clone DEIN-REPO .
pip install -r voice_assistant_requirements.txt

# Environment Variables
sudo nano /opt/voice-assistant/.env
```

### Systemd Service

**`/etc/systemd/system/voice-assistant.service`:**
```ini
[Unit]
Description=Voice Assistant
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/voice-assistant
Environment=PATH=/opt/voice-assistant/venv/bin
ExecStart=/opt/voice-assistant/venv/bin/python voice_assistant_server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Nginx Proxy

**`/etc/nginx/sites-available/voice-assistant`:**
```nginx
server {
    listen 80;
    server_name DEINE-DOMAIN.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL mit Let's Encrypt

```bash
# Certbot installieren
sudo apt install certbot python3-certbot-nginx -y

# SSL Zertifikat
sudo certbot --nginx -d DEINE-DOMAIN.com
```

### Service starten

```bash
# Service aktivieren
sudo systemctl enable voice-assistant
sudo systemctl start voice-assistant

# Nginx konfigurieren
sudo ln -s /etc/nginx/sites-available/voice-assistant /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

**Kosten**: $5-50/Monat

---

## 🌊 DigitalOcean

### App Platform (Einfach)

1. **DigitalOcean Account**
2. **App Platform nutzen**

**`.do/app.yaml`:**
```yaml
name: voice-assistant
services:
- name: web
  source_dir: /
  github:
    repo: DEIN-REPO
    branch: main
  run_command: python voice_assistant_server.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: OPENAI_API_KEY
    value: sk-proj-...
  - key: DEEPGRAM_API_KEY
    value: ...
  - key: ELEVENLABS_API_KEY
    value: ...
  - key: TWILIO_ACCOUNT_SID
    value: AC...
  - key: TWILIO_AUTH_TOKEN
    value: ...
  http_port: 8000
```

**Kosten**: $5-25/Monat

### Droplet (Manuell)

Ähnlich wie AWS EC2, aber mit Ubuntu 22.04:

```bash
# Droplet erstellen (1GB RAM minimum)
# SSH verbinden und gleicher Prozess wie AWS
```

---

## ⚡ Azure Container Instances

### Setup

```bash
# Azure CLI
az login
az group create --name voice-assistant-rg --location eastus
```

### Container Deployment

```bash
# Container Image bauen (lokal oder Azure Container Registry)
docker build -t voice-assistant .

# Azure Container Registry (optional)
az acr create --resource-group voice-assistant-rg --name voiceassistant --sku Basic
az acr build --registry voiceassistant --image voice-assistant .

# Container Instance erstellen
az container create \
  --resource-group voice-assistant-rg \
  --name voice-assistant \
  --image voice-assistant \
  --dns-name-label voice-assistant-unique \
  --ports 8000 \
  --environment-variables \
    OPENAI_API_KEY=sk-proj-... \
    DEEPGRAM_API_KEY=... \
    ELEVENLABS_API_KEY=... \
    TWILIO_ACCOUNT_SID=AC... \
    TWILIO_AUTH_TOKEN=...
```

**Kosten**: $10-30/Monat

---

## 🔒 Produktions-Sicherheit

### SSL/HTTPS

Alle Deployments **MÜSSEN** HTTPS verwenden:

- **Railway/Heroku**: Automatisch SSL
- **Cloud Run**: Automatisch SSL
- **Eigener Server**: Let's Encrypt verwenden

### Environment Variables

❌ **NIE in Code committen:**
```python
# FALSCH
api_key = "sk-proj-abcd1234..."
```

✅ **Immer Environment Variables:**
```python
# RICHTIG
api_key = os.getenv("OPENAI_API_KEY")
```

### Rate Limiting

**FastAPI Middleware hinzufügen:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/webhook/twilio")
@limiter.limit("10/minute")
async def twilio_webhook(request: Request):
    # ...
```

### Monitoring

**Health Checks aktivieren:**
- `/health` Endpoint nutzen
- Uptime-Monitoring (UptimeRobot, Pingdom)
- Log-Aggregation (Sentry, LogRocket)

---

## 📊 Kosten-Übersicht

| Provider | Monatliche Kosten | Setup-Zeit | Schwierigkeit |
|----------|------------------|------------|---------------|
| Railway | $5-20 | 10 min | ⭐ |
| Heroku | $7-25 | 15 min | ⭐⭐ |
| Google Cloud Run | $0-20 | 20 min | ⭐⭐⭐ |
| DigitalOcean App | $5-25 | 15 min | ⭐⭐ |
| AWS EC2 | $5-50 | 45 min | ⭐⭐⭐⭐ |
| Azure Container | $10-30 | 30 min | ⭐⭐⭐ |

**Empfehlung**: Railway für Prototypen, AWS/Google Cloud für Enterprise

---

## 🆘 Troubleshooting

### Häufige Probleme

**1. WebSocket Verbindungen fehlschlagen**
```bash
# Prüfen ob WebSocket Support aktiviert ist
curl -H "Upgrade: websocket" https://DEINE-DOMAIN.com/ws/twilio
```

**2. SSL-Zertifikat Probleme**
```bash
# SSL Status prüfen
openssl s_client -connect DEINE-DOMAIN.com:443
```

**3. Performance Probleme**
- Mindestens 1GB RAM
- CPU-optimierte Instance-Typen
- Redis für Session-Storage bei hohem Traffic

### Logs überwachen

**Heroku:**
```bash
heroku logs --tail --app voice-assistant-app
```

**Railway:**
```bash
railway logs --follow
```

**AWS/DigitalOcean:**
```bash
sudo journalctl -u voice-assistant -f
```

---

## 📞 Twilio Webhook Konfiguration

Nach dem Deployment:

1. **Twilio Console**: https://console.twilio.com/
2. **Phone Numbers** → Ihre Nummer auswählen
3. **Webhook URL**: `https://DEINE-DOMAIN.com/webhook/twilio`
4. **HTTP Method**: POST
5. **Speichern**

**Test**: Rufen Sie Ihre Twilio-Nummer an! 🎉

---

## 🎯 Nächste Schritte

1. **Monitoring einrichten** (Sentry, DataDog)
2. **Analytics hinzufügen** (Anruf-Statistiken)
3. **A/B Testing** (verschiedene Prompts)
4. **Auto-Scaling** konfigurieren
5. **Backup-Strategien** implementieren

Bei Fragen: Issues im Repository erstellen! 🙋‍♂️