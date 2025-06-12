from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from lib.navigation import tombol_menu_utama

async def handle_portal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Daftar Halaqah", callback_data="daftar_halaqah")],
        [InlineKeyboardButton("🪪 Lihat Santri", callback_data="lihat_santri")],
        [InlineKeyboardButton("📝 Rekap Bulanan", callback_data="rekap_bulanan")],
    ]

    keyboard += tombol_menu_utama().inline_keyboard
    reply_markup = InlineKeyboardMarkup(keyboard)

    pesan = "Silakan pilih menu di bawah ini."

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=pesan,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
