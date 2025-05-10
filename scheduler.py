import os
import time
import random
import threading
import requests

from memory.memory_handler import memory, get_history

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("DEBUG_CHAT_ID")  # для теста можно вручную задать ID
CHECK_INTERVAL = 300  # каждые 5 минут

def importance_score():
    """
    Простейшая эвристика оценки важности сообщения:
    - чем дольше молчание, тем выше счёт
    - можно улучшать: по эмоциям, теме и т.д.
    """
    history = get_history()
    if not history:
        return 0
    silence_weight = min(len(history) * 0.5, 5)
    random_factor = random.uniform(0, 3)
    return silence_weight + random_factor

def maybe_send_message():
    score = importance_score()
    threshold = 4.5  # настраиваемый порог
    if score >= threshold:
        send_message("Я подумал, что стоит кое-что тебе сказать...")

def send_message(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

def run_scheduler():
    while True:
        maybe_send_message()
        time.sleep(CHECK_INTERVAL)

# Запускаем в фоне
def start_scheduler():
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
