from telegram import Update
from telegram.ext import ContextTypes
from lib.navigation import tombol_menu_utama

async def handle_galeri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pesan = (
        "🖼️ *Galeri PPTQ Al-Itqon Gowa*\n\n"
        "Berikut adalah dokumentasi kegiatan Pondok dalam bentuk foto dan video. Silakan akses melalui link di bawah ini:\n\n"
        "🔗 https://drive.google.com/drive/folders/1642Sydp5EXFtsStmKvaCWl93VAs6HSDf\n\n"
        "Folder sudah dikelompokkan berdasarkan kegiatan.\n"
        "📌 Silakan buka melalui browser untuk tampilan terbaik.\n\n"
        "_Barakallahu fiikum!_"
    )

    await query.edit_message_text(
        text=pesan,
        parse_mode="Markdown",
        reply_markup=tombol_menu_utama()
    )
