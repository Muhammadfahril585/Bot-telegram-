from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from lib.navigation import tombol_menu_utama

async def handle_tentang_kami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏫 Profil Pondok", callback_data="profil_pondok")],
        [InlineKeyboardButton("🎯 Visi Misi", callback_data="visi_misi")],
        [InlineKeyboardButton("🧩 Struktur Organisasi", callback_data="struktur")],
    ]

    keyboard += tombol_menu_utama().inline_keyboard
    reply_markup = InlineKeyboardMarkup(keyboard)

    pesan = (
        "📌 <b>Tentang Kami</b>\n\n"
        "Silakan pilih salah satu menu di bawah:"
    )

    await update.callback_query.edit_message_text(
        text=pesan,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

