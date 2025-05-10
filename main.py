from flask import Flask, request
import os
import requests

app = Flask(__name__)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
LOCAL_LLM_API = "http://127.0.0.1:8000/v1/chat/completions"  # твой локальный Hermes

@app.route('/', methods=['GET'])
def home():
    return 'Hermes Memory Bot is running.'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Формируем запрос к Hermes 2
        payload = {
            "model": "nous-hermes-llama-2-7b",
            "messages": [
                {"role": "user", "content": text}
            ]
        }

        try:
            response = requests.post(LOCAL_LLM_API, json=payload)
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"Ошибка ответа от модели: {e}"

        # Отправляем ответ пользователю
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply
        })

    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

from scheduler import start_scheduler
start_scheduler()
