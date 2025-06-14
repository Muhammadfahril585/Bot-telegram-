from telegram import Update
from telegram.ext import ContextTypes

ADMIN_CHAT_ID = 970201320  # Ganti dengan chat ID kamu (pastikan dalam bentuk integer, bukan string)

async def track_user_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name or ""
    username = f"@{user.username}" if user.username else "(tidak ada username)"
    user_id = user.id

    text = (
        f"Bot sedang diakses:\n"
        f"Nama: {first_name}\n"
        f"Username: {username}\n"
        f"User ID: {user_id}"
    )
