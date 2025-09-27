# handlers/wa_bridge.py
import os
import re
import logging
import requests
from typing import Optional

from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, Application

log = logging.getLogger(__name__)

GAS_URL = os.getenv("GAS_URL")  # ex: https://script.google.com/macros/s/.../exec
BRIDGE_SECRET = os.getenv("BRIDGE_SECRET", "rahasia-bridge")

# (Opsional) batasi siapa yg boleh membalas, isi comma-separated user id Telegram
# contoh env: ALLOWED_REPLY_USER_IDS="12345,67890"
_ALLOWED = {s.strip() for s in os.getenv("ALLOWED_REPLY_USER_IDS", "").split(",") if s.strip()}


def _extract_wa_jid(txt: str) -> Optional[str]:
    if not txt:
        return None
    m = re.search(r"wa_jid:\s*(\S+)", txt)
    return m.group(1) if m else None


async def _on_reply_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    if not msg.reply_to_message or not msg.reply_to_message.text:
        return

    # Security: optional allowlist
    if _ALLOWED and str(update.effective_user.id) not in _ALLOWED:
        return  # diam-diam abaikan

    wa_jid = _extract_wa_jid(msg.reply_to_message.text)
    if not wa_jid:
        return  # hanya proses balasan ke pesan yg ada header wa_jid

    if not GAS_URL:
        await msg.reply_text("❌ GAS_URL belum diset di environment.")
        return

    payload = {
        "secret": BRIDGE_SECRET,
        "wa_jid": wa_jid,
        "text": msg.text,
        "requested_by": str(update.effective_user.id),
    }

    try:
        r = requests.post(f"{GAS_URL}?path=queue-outbound", json=payload, timeout=12)
        r.raise_for_status()
        await msg.reply_text("✅ Dimasukkan antrian ke WA")
    except Exception as e:
        log.exception("queue-outbound failed")
        await msg.reply_text(f"❌ Gagal antri ke WA: {e}")


def wa_reply_handler() -> MessageHandler:
    """
    Kembalikan handler yg siap ditambahkan ke Application.
    Hanya memproses TEXT (bukan command) & yang merupakan reply.
    """
    return MessageHandler(filters.TEXT & ~filters.COMMAND, _on_reply_forward)


def register_wa_bridge(app: Application) -> None:
    """
    Alternatif: langsung daftarkan ke Application.
    """
    app.add_handler(wa_reply_handler())
