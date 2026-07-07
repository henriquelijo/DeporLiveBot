# src/adapters/telegram_bot.py
import json
import urllib.request
from datetime import datetime
from src.ports.notifier import Notifier

class TelegramBotAdapter(Notifier):
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"

    def send_notification(self, text: str) -> None:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Enviando mensaje a Telegram: {text.replace('<br>', ' ')}")
        if not text:
            return

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.url, data=data, method="POST")
        req.add_header("Content-Type", "application/json; charset=utf-8")
        req.add_header("Content-Length", len(data))
        req.add_header("User-Agent", "PostmanRuntime/7.32.3")
        
        try:
            with urllib.request.urlopen(req) as response:
                response.read()
        except Exception as e:
            print(f"Error en Telegram: {e}")