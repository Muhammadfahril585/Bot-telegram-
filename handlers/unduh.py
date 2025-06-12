from telegram import Update
from telegram.ext import ContextTypes
from lib.navigation import tombol_menu_utama

async def handle_unduh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pesan = (
        "*📁 Unduh Berkas Penting*\n\n"
        "Berikut beberapa file penting yang bisa Anda unduh:\n\n"
        "1. 📄 *Formulir Pendaftaran Santri Baru (PSB)*\n"
        "   [Klik untuk unduh](https://drive.google.com/file/d/1A5x3STzOYdEKsLG2aO7ebfhcWLjXNjqF/view?usp=drivesdk)\n\n"
        "2. 🗓️ *Jadwal Kegiatan Harian Santri*\n"
        "   [Klik untuk unduh](https://drive.google.com/file/d/19khdCbyrtZglMeihLwZTXyl2DsWrpAES/view?usp=drivesdk)\n\n"
        "Silakan klik tautan untuk melihat atau mengunduh file.\n"
        "_Barakallahu fiikum._"
    )

    await query.edit_message_text(
        text=pesan,
        parse_mode="Markdown",
        reply_markup=tombol_menu_utama()
    )
