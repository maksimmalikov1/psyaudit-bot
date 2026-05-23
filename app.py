import hashlib
import hmac
import logging
import os

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
PRODAMUS_SECRET_KEY = os.environ["PRODAMUS_SECRET_KEY"]
PAYFORM_URL = "https://payform.ru/6bbzNr3/"

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage",
                  json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)


def create_invite_link():
    resp = requests.post(f"{TELEGRAM_API}/createChatInviteLink",
                         json={"chat_id": CHANNEL_ID, "member_limit": 1}, timeout=10)
    return resp.json()["result"]["invite_link"]


def verify_signature(payload, provided_sign):
    pairs = sorted((k, v) for k, v in payload.items() if k != "sign")
    message = "&".join(f"{k}={v}" for k, v in pairs)
    expected = hmac.new(PRODAMUS_SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, provided_sign)


@app.route("/tg", methods=["POST"])
def tg():
    update = request.get_json()
    message = update.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    if text == "/start" and chat_id:
        pay_link = f"{PAYFORM_URL}?customer_extra={chat_id}"
        send_message(chat_id,
            f"Здравствуйте! \n\n"
            f"Вы создали заказ: Онлайн курс «Психологический Чекап»\n"
            f"Сумма заказа: 5900 руб.\n\n"
            f"Чтобы оплатить заказ, перейдите по ссылке:\n{pay_link}\n\n"
            f"Если у вас появятся вопросы, пишите: info_malikova@internet.ru")
    return jsonify({"ok": True}), 200


@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.form.to_dict()
    sign = payload.get("sign", "")
    if not sign or not verify_signature(payload, sign):
        return jsonify({"error": "invalid signature"}), 403
    if payload.get("payment_status") != "success":
        return jsonify({"status": "ignored"}), 200
    telegram_id = payload.get("customer_extra") or payload.get("telegram_id")
    if not telegram_id:
        return jsonify({"error": "no telegram_id"}), 400
    try:
        link = create_invite_link()
        send_message(telegram_id,
            f"Оплата подтверждена! 🎉\n\n"
            f"Ваша персональная одноразовая ссылка для вступления в канал:\n{link}")
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        log.exception("Error: %s", e)
        return jsonify({"error": "internal error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
