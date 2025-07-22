from telegram import Update
from telegram.ext import ContextTypes
from lib.knowledge_engine import jawab_berbasis_pengetahuan
from handlers.start import get_user_mode  # Cek mode user

async def handle_ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Cek apakah user sedang dalam mode AI
    if get_user_mode(user_id) != "ai":
        return

    # Serahkan pertanyaan ke mesin pengetahuan
    await jawab_berbasis_pengetahuan(update, context)
