from flask import Flask, request
import os
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

LLM_API_URL = os.environ.get("LLM_API_URL")  # например: http://65.108.12.23:8000/v1/chat/completions

@app.route('/', methods=['GET'])
def home():
    return 'Hermes bot is active'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_msg = data["message"].get("text", "")

        # Формируем запрос к локальной LLM
        try:
            response = requests.post(LLM_API_URL, json={
                "model": "nous-hermes-llama-2-7b",
                "messages": [
                    {"role": "user", "content": user_msg}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }, timeout=60)

            if response.status_code == 200:
                ai_reply = response.json()["choices"][0]["message"]["content"].strip()
            else:
                ai_reply = "Ошибка генерации ответа (код {})".format(response.status_code)

        except Exception as e:
            ai_reply = f"Ошибка соединения с ИИ: {e}"

        # Отправляем ответ в Telegram
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": ai_reply
        })

    return '', 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
