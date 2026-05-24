import hashlib
import hmac
import json
import logging
import os
import re

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
# phone → chat_id mapping, persisted to JSON so it survives restarts
# ---------------------------------------------------------------------------
PHONE_MAP_PATH = "/tmp/phone_map.json"


def _load_phone_map() -> dict[str, str]:
    try:
        with open(PHONE_MAP_PATH, encoding="utf-8") as f:
            data = json.load(f)
            log.info("Loaded %d phone mappings from %s", len(data), PHONE_MAP_PATH)
            return data
    except FileNotFoundError:
        log.info("No phone_map file found at %s, starting fresh", PHONE_MAP_PATH)
        return {}
    except Exception:
        log.exception("Failed to load phone_map from %s, starting fresh", PHONE_MAP_PATH)
        return {}


def _save_phone_map() -> None:
    try:
        with open(PHONE_MAP_PATH, "w", encoding="utf-8") as f:
            json.dump(phone_map, f, ensure_ascii=False, indent=2)
        log.info("phone_map saved to %s (%d entries)", PHONE_MAP_PATH, len(phone_map))
    except Exception:
        log.exception("Failed to save phone_map to %s", PHONE_MAP_PATH)


phone_map: dict[str, str] = {}  # populated below after logging is configured

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

phone_map = _load_phone_map()  # load after logger is ready


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_phone(phone: str) -> str:
    """Strip everything except digits (handles +7, 8, spaces, dashes, etc.)."""
    return re.sub(r"\D", "", phone)


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


def send_message(chat_id: str, text: str, reply_markup: dict | None = None) -> None:
    """Send a plain HTML message to a Telegram user, with optional reply_markup."""
    body: dict = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup is not None:
        body["reply_markup"] = reply_markup
    resp = requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json=body,
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
    # Prodamus sends JSON body; signature is in the "Sign" request header
    payload = request.get_json(silent=True)
    if payload is None:
        log.warning("Request rejected: body is not valid JSON")
        return jsonify({"error": "invalid JSON body"}), 400
    log.info("Incoming webhook payload: %s", payload)

    # 1. Signature verification
    sign = request.headers.get("Sign", "")
    if not sign:
        log.warning("Request rejected: missing 'Sign' header")
        return jsonify({"error": "missing signature"}), 400

    if not verify_signature(payload, sign):
        log.warning("Request rejected: signature mismatch")
        return jsonify({"error": "invalid signature"}), 403

    # 2. Only act on successful payments
    payment_status = payload.get("payment_status", "")
    if payment_status != "success":
        log.info("Skipping event with payment_status=%r", payment_status)
        return jsonify({"status": "ignored"}), 200

    # 3. Resolve customer chat_id from phone number
    raw_phone = payload.get("customer_phone", "")
    if not raw_phone:
        log.error("No customer_phone in payload: %s", payload)
        return jsonify({"error": "no customer_phone in payload"}), 400

    phone = normalize_phone(raw_phone)
    chat_id = phone_map.get(phone)
    if not chat_id:
        log.error("Phone not found in mapping: %s", phone)
        return jsonify({"error": "phone not found in mapping"}), 400

    # 4. Create invite link and notify the customer
    try:
        link = create_invite_link()
        order_id = payload.get("order_id", "—")
        log.info("Created invite link for order %s, phone %s, chat %s: %s",
                 order_id, phone, chat_id, link)

        send_message(
            chat_id,
            f"Оплата подтверждена!\n\n"
            f"Заказ: <b>{order_id}</b>\n\n"
            f"Ваша персональная одноразовая ссылка для вступления в канал:\n"
            f"{link}",
        )
        log.info("Invite link sent to chat %s", chat_id)
        return jsonify({"status": "ok"}), 200

    except Exception:
        log.exception("Error while processing webhook for chat_id=%s", chat_id)
        return jsonify({"error": "internal error"}), 500


# ---------------------------------------------------------------------------
# Telegram bot endpoint
# ---------------------------------------------------------------------------

@app.route("/tg", methods=["POST"])
def tg():
    update = request.get_json(silent=True)
    if not update:
        return jsonify({"error": "empty body"}), 400

    log.info("Telegram update: %s", update)

    message = update.get("message", {})
    chat_id = str(message.get("chat", {}).get("id", ""))

    if not chat_id:
        return jsonify({"status": "no chat_id"}), 200

    # ── /start: ask user to share phone number ────────────────────────────
    text = message.get("text", "")
    if text.startswith("/start"):
        keyboard = {
            "keyboard": [[{"text": "Поделиться номером телефона", "request_contact": True}]],
            "resize_keyboard": True,
            "one_time_keyboard": True,
        }
        try:
            send_message(
                chat_id,
                "Здравствуйте!\n\n"
                "Для получения доступа к каналу после оплаты нам нужно связать ваш "
                "номер телефона с этим чатом.\n\n"
                "Нажмите кнопку ниже, чтобы поделиться номером.",
                reply_markup=keyboard,
            )
            log.info("Sent contact request to user %s", chat_id)
        except Exception:
            log.exception("Failed to send contact request to user %s", chat_id)
        return jsonify({"status": "ok"}), 200

    # ── contact shared: save phone → chat_id mapping ──────────────────────
    contact = message.get("contact")
    if contact:
        raw_phone = contact.get("phone_number", "")
        phone = normalize_phone(raw_phone)
        if phone:
            phone_map[phone] = chat_id
            log.info("Saved phone mapping: %s → %s", phone, chat_id)
            _save_phone_map()
            try:
                send_message(
                    chat_id,
                    "Отлично! Ваш номер сохранён. Теперь перейдите к оплате курса по ссылке: "
                    "https://payform.ru/6bbzNr3/\n\n"
                    "После оплаты вы автоматически получите ссылку в этот чат.",
                    reply_markup={"remove_keyboard": True},
                )
                log.info("Sent payment link to user %s (phone %s)", chat_id, phone)
            except Exception:
                log.exception("Failed to send confirmation to user %s", chat_id)
        else:
            log.warning("Received empty phone from contact update for chat %s", chat_id)

    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------------
# Local dev only — PythonAnywhere uses the WSGI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)


