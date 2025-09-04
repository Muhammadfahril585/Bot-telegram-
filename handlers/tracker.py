# handlers/track_user.py
from html import escape as h
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

ADMIN_CHAT_ID = 970201320  # pastikan integer

async def track_user_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:  # jaga-jaga
        return

    first_name = h(user.first_name or "")
    username = f"@{user.username}" if user.username else "(tidak ada username)"
    user_id = user.id
    deep_link = f"tg://user?id={user_id}"

    # Teks log (HTML biar rapi + ada link klik)
    text = (
        f"<b>Bot sedang diakses:</b>\n"
        f"Nama: {first_name}\n"
        f"Username: {username}\n"
        f"User ID: <code>{user_id}</code>\n"
        f"Profil/Chat: <a href=\"{deep_link}\">Buka chat</a>"
    )

    # Inline keyboard: tombol “Buka chat”
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Buka chat", url=deep_link)]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
