#
# Lokaler Entwicklungshelfer für Voice Assistant
# Automatisiert das Setup für lokale Tests mit ngrok
#

import os
import sys
import subprocess
import time
import asyncio
import json
import signal
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(override=True)


class LocalDevSetup:
    def __init__(self):
        self.ngrok_process = None
        self.server_process = None
        self.ngrok_url = None

    def check_dependencies(self):
        """Prüft ob alle benötigten Tools installiert sind"""
        print("🔍 Prüfe Abhängigkeiten...")

        # ngrok prüfen
        try:
            result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ ngrok gefunden: {result.stdout.strip()}")
            else:
                print("❌ ngrok nicht gefunden oder funktioniert nicht")
                return False
        except FileNotFoundError:
            print("❌ ngrok nicht installiert")
            print("   Installieren Sie ngrok von: https://ngrok.com/download")
            print("   Oder mit chocolatey: choco install ngrok")
            return False

        # Python Dependencies prüfen
        try:
            import uvicorn
            import fastapi
            print("✅ FastAPI und uvicorn verfügbar")
        except ImportError:
            print("❌ FastAPI/uvicorn nicht installiert")
            print("   Führen Sie aus: pip install -r voice_assistant_requirements.txt")
            return False

        return True

    def start_ngrok(self, port=8000):
        """Startet ngrok und gibt die öffentliche URL zurück"""
        print(f"🌐 Starte ngrok für Port {port}...")

        try:
            # ngrok im Hintergrund starten
            self.ngrok_process = subprocess.Popen(
                ["ngrok", "http", str(port), "--log=stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Kurz warten damit ngrok startet
            time.sleep(3)

            # ngrok API abfragen für die URL
            try:
                import requests
                response = requests.get("http://127.0.0.1:4040/api/tunnels")
                tunnels = response.json()

                if tunnels.get("tunnels"):
                    public_url = tunnels["tunnels"][0]["public_url"]
                    # Stelle sicher, dass wir https verwenden
                    if public_url.startswith("http://"):
                        public_url = public_url.replace("http://", "https://")

                    self.ngrok_url = public_url
                    print(f"✅ ngrok läuft: {public_url}")
                    return public_url
                else:
                    print("❌ Keine ngrok Tunnels gefunden")
                    return None

            except Exception as e:
                print(f"❌ Fehler beim Abrufen der ngrok URL: {e}")
                print("   Prüfen Sie ob ngrok korrekt läuft: http://127.0.0.1:4040")
                return None

        except Exception as e:
            print(f"❌ Fehler beim Starten von ngrok: {e}")
            return None

    def update_env_file(self, ngrok_url):
        """Aktualisiert die .env Datei mit der ngrok URL"""
        env_file = Path(".env")

        if not env_file.exists():
            print("⚠️ .env Datei nicht gefunden, erstelle eine basierend auf .env.example")
            # Kopiere .env.example nach .env
            example_file = Path(".env.example")
            if example_file.exists():
                content = example_file.read_text()
                env_file.write_text(content)
            else:
                print("❌ .env.example auch nicht gefunden!")
                return False

        # SERVER_DOMAIN in .env aktualisieren
        content = env_file.read_text()
        lines = content.split('\n')

        # ngrok URL ohne https:// für SERVER_DOMAIN
        domain = ngrok_url.replace("https://", "").replace("http://", "")

        updated = False
        for i, line in enumerate(lines):
            if line.startswith("SERVER_DOMAIN="):
                lines[i] = f"SERVER_DOMAIN={domain}"
                updated = True
                break

        if not updated:
            lines.append(f"SERVER_DOMAIN={domain}")

        env_file.write_text('\n'.join(lines))
        print(f"✅ .env aktualisiert: SERVER_DOMAIN={domain}")
        return True

    def start_server(self):
        """Startet den Voice Assistant Server"""
        print("🚀 Starte Voice Assistant Server...")

        try:
            self.server_process = subprocess.Popen([
                sys.executable, "voice_assistant_server.py"
            ])
            time.sleep(2)  # Kurz warten

            # Prüfen ob Server läuft
            if self.server_process.poll() is None:
                print("✅ Voice Assistant Server gestartet")
                return True
            else:
                print("❌ Server konnte nicht gestartet werden")
                return False

        except Exception as e:
            print(f"❌ Fehler beim Starten des Servers: {e}")
            return False

    def show_setup_instructions(self):
        """Zeigt die finalen Setup-Anweisungen"""
        if not self.ngrok_url:
            return

        webhook_url = f"{self.ngrok_url}/webhook/twilio"

        print("\n" + "="*60)
        print("🎉 LOKALE ENTWICKLUNGSUMGEBUNG BEREIT!")
        print("="*60)
        print(f"🌐 Öffentliche URL: {self.ngrok_url}")
        print(f"📞 Twilio Webhook: {webhook_url}")
        print(f"🔍 Gesundheitscheck: {self.ngrok_url}/health")
        print(f"⚙️ Konfiguration: {self.ngrok_url}/config")

        print("\n📋 TWILIO SETUP:")
        print("1. Gehen Sie zu: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
        print("2. Wählen Sie Ihre Telefonnummer aus")
        print("3. Webhook URL eintragen:")
        print(f"   {webhook_url}")
        print("4. HTTP Method: POST")
        print("5. Speichern")

        print("\n🧪 TESTS:")
        print("- Rufen Sie Ihre Twilio-Nummer an")
        print("- Prüfen Sie die Logs in diesem Terminal")
        print(f"- Besuchen Sie {self.ngrok_url}/health für Status")

        print("\n⚠️ WICHTIG:")
        print("- Diese ngrok URL ist nur temporär!")
        print("- Bei jedem Neustart ändert sich die URL")
        print("- Für Produktion: Nutzen Sie einen Cloud-Service")

        print("\n🛑 ZUM BEENDEN:")
        print("- Drücken Sie Ctrl+C in diesem Terminal")

    def cleanup(self):
        """Räumt auf und beendet alle Prozesse"""
        print("\n🧹 Beende Entwicklungsumgebung...")

        if self.server_process:
            print("   - Beende Voice Assistant Server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()

        if self.ngrok_process:
            print("   - Beende ngrok...")
            self.ngrok_process.terminate()
            try:
                self.ngrok_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ngrok_process.kill()

        print("✅ Cleanup abgeschlossen")

    def run(self):
        """Hauptfunktion - startet die komplette lokale Entwicklungsumgebung"""
        print("Voice Assistant - Lokale Entwicklungsumgebung")
        print("="*60)

        # Signal Handler für sauberes Beenden
        def signal_handler(sig, frame):
            print(f"\n📡 Signal {sig} empfangen...")
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            # 1. Dependencies prüfen
            if not self.check_dependencies():
                return False

            # 2. ngrok starten
            ngrok_url = self.start_ngrok()
            if not ngrok_url:
                return False

            # 3. .env aktualisieren
            if not self.update_env_file(ngrok_url):
                return False

            # 4. Server starten
            if not self.start_server():
                return False

            # 5. Setup-Anweisungen anzeigen
            self.show_setup_instructions()

            # 6. Auf Beenden warten
            print("\n⏳ Drücken Sie Ctrl+C zum Beenden...")
            try:
                while True:
                    time.sleep(1)
                    # Prüfen ob Prozesse noch laufen
                    if self.server_process and self.server_process.poll() is not None:
                        print("❌ Server ist unerwartet beendet worden")
                        break
                    if self.ngrok_process and self.ngrok_process.poll() is not None:
                        print("❌ ngrok ist unerwartet beendet worden")
                        break
            except KeyboardInterrupt:
                pass

        except Exception as e:
            print(f"❌ Unerwarteter Fehler: {e}")
            return False
        finally:
            self.cleanup()

        return True


if __name__ == "__main__":
    setup = LocalDevSetup()
    success = setup.run()
    sys.exit(0 if success else 1)