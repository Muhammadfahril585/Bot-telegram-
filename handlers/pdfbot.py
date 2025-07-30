from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def handle_pdfbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 Buka Office2PDF Bot", url="https://t.me/office2pdf_supportbot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Silakan tekan tombol di bawah ini untuk *Mengubah ah Gambar ke PDF* 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
