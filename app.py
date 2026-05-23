import hashlib
import hmac
import logging
import os

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Config — set these as environment variables (see deployment instructions)
# ---------------------------------------------------------------------------
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]          # e.g. -1001234567890
PRODAMUS_SECRET_KEY = os.environ["PRODAMUS_SECRET_KEY"]

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webhook.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(_log_path, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def verify_signature(payload: dict, provided_sign: str) -> bool:
    """
    Prodamus signs the payload with HMAC-SHA256.
    Build a sorted key=value string (excluding the 'sign' field itself),
    compute the expected signature, and compare in constant time.
    """
    pairs = sorted((k, v) for k, v in payload.items() if k != "sign")
    message = "&".join(f"{k}={v}" for k, v in pairs)
    expected = hmac.new(
        PRODAMUS_SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, provided_sign)


def create_invite_link() -> str:
    """Create a one-time Telegram invite link (member_limit=1)."""
    resp = requests.post(
        f"{TELEGRAM_API}/createChatInviteLink",
        json={"chat_id": CHANNEL_ID, "member_limit": 1},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram createChatInviteLink failed: {data}")
    return data["result"]["invite_link"]


def send_message(chat_id: str, text: str) -> None:
    """Send a plain HTML message to a Telegram user."""
    resp = requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {data}")


# ---------------------------------------------------------------------------
# Webhook endpoint
# ---------------------------------------------------------------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    # Prodamus sends application/x-www-form-urlencoded
    payload = request.form.to_dict()
    log.info("Incoming webhook payload: %s", payload)

    # 1. Signature verification
    sign = payload.get("sign", "")
    if not sign:
        log.warning("Request rejected: missing 'sign' field")
        return jsonify({"error": "missing signature"}), 400

    if not verify_signature(payload, sign):
        log.warning("Request rejected: signature mismatch")
        return jsonify({"error": "invalid signature"}), 403

    # 2. Only act on successful payments
    payment_status = payload.get("payment_status", "")
    if payment_status != "success":
        log.info("Skipping event with payment_status=%r", payment_status)
        return jsonify({"status": "ignored"}), 200

    # 3. Resolve customer Telegram ID
    # Pass it from Prodamus as a custom field named 'telegram_id'
    # (see deployment instructions for how to append it to the payment link URL)
    telegram_id = payload.get("telegram_id") or payload.get("sys_telegram_id")
    if not telegram_id:
        log.error("No telegram_id found in payload: %s", payload)
        return jsonify({"error": "no telegram_id in payload"}), 400

    # 4. Create invite link and notify the customer
    try:
        link = create_invite_link()
        order_id = payload.get("order_id", "—")
        log.info("Created invite link for order %s, user %s: %s", order_id, telegram_id, link)

        send_message(
            telegram_id,
            f"Оплата подтверждена!\n\n"
            f"Заказ: <b>{order_id}</b>\n\n"
            f"Ваша персональная одноразовая ссылка для вступления в канал:\n"
            f"{link}",
        )
        log.info("Invite link sent to Telegram user %s", telegram_id)
        return jsonify({"status": "ok"}), 200

    except Exception:
        log.exception("Error while processing webhook for telegram_id=%s", telegram_id)
        return jsonify({"error": "internal error"}), 500


# ---------------------------------------------------------------------------
# Local dev only — PythonAnywhere uses the WSGI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
