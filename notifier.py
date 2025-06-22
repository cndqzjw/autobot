import requests
from config import config

def send_telegram(message):
    url = f"https://api.telegram.org/bot{config['telegram_token']}/sendMessage"
    payload = {
        'chat_id': config['telegram_chat_id'],
        'text': message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("[ERROR] Failed to send Telegram message:", e)