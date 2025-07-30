from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def handle_quran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Buka Qur'an Bot", url="https://t.me/qidbot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📖 *Silakan tekan tombol di bawah ini untuk membuka Qur'an Bot* 👇\n\n"
        "Setelah terbuka, kamu bisa ketik perintah: `/Juz_1` untuk mulai membaca.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
