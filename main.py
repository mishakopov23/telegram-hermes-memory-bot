from flask import Flask, request
import os
import requests

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
LLM_API_URL = os.environ.get("LLM_API_URL")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/', methods=['GET'])
def home():
    return 'Hermes Memory Bot is running.'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        # Отправляем текст локальной модели через API
        try:
            response = requests.post(LLM_API_URL, json={
                "model": "nous-hermes-llama-2-7b",
                "messages": [{"role": "user", "content": user_text}],
                "temperature": 0.7,
                "max_tokens": 100
            })

            if response.status_code == 200:
                reply_text = response.json()["choices"][0]["message"]["content"]
            else:
                reply_text = "Ошибка при получении ответа от модели."

        except Exception as e:
            reply_text = f"Ошибка: {str(e)}"

        # Отправляем ответ пользователю в Telegram
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply_text
        })
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
