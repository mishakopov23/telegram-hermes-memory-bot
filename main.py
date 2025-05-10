from flask import Flask, request
import os
import requests

app = Flask(__name__)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/', methods=['GET'])
def home():
    return 'Hermes Memory Bot is running.'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        reply = f"Ты написал: {text}"
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply
        })
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

