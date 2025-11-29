# handlers/ai_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from lib.knowledge_engine import proses_pertanyaan_ai


async def handle_ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Dipanggil untuk SEMUA pesan teks yang bukan command.
    AI langsung memberikan jawaban.
    """
    if not update.message or not update.message.text:
        return

    pertanyaan = update.message.text.strip()
    if not pertanyaan:
        return

    await proses_pertanyaan_ai(update, context, pertanyaan)
