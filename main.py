from flask import Flask, request
import os
import requests

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
LLM_API_URL = os.environ.get("LLM_API_URL", "http://127.0.0.1:8000/v1/chat/completions")

@app.route('/', methods=['GET'])
def home():
    return 'Hermes Memory Bot is running.'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        payload = {
            "model": "nous-hermes-llama-2-7b",
            "messages": [{"role": "user", "content": text}],
            "temperature": 0.7,
            "max_tokens": 500
        }

        try:
            response = requests.post(LLM_API_URL, json=payload)
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"Ошибка: {e}"

        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply
        })
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
