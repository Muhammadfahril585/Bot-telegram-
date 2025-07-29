from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def handle_quran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📖 Buka Juz 1 di Bot Tafsir", url="https://t.me/qidbot?start=Juz_1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Silakan tekan tombol di bawah ini 👇",
        reply_markup=reply_markup
    )
