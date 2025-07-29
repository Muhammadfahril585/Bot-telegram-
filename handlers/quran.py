from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

keyboard = [
    [InlineKeyboardButton("🚀 Buka Qur'an Bot", url="https://t.me/qidbot")]
]
reply_markup = InlineKeyboardMarkup(keyboard)

await update.message.reply_text(
    "Silakan tekan tombol di bawah ini untuk membuka Qur'an Bot 👇\nSetelah terbuka, ketik perintah: /Juz_1",
    reply_markup=reply_markup
)
