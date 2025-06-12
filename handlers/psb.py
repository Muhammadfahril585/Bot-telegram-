from telegram import Update
from telegram.ext import ContextTypes
from lib.navigation import tombol_menu_utama

async def handle_psb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pesan = (
        "📝 *PENDAFTARAN SANTRI BARU (PSB)*\n\n"
        "Informasi seputar pendaftaran santri baru saat ini *masih dalam pengembangan*.\n\n"
        "Untuk sementara, silakan hubungi kontak admin untuk pertanyaan lebih lanjut:\n"
        "📞 *+6285298514896* (Ustadz Laode Muh Fahril)\n\n"
        "_Terima kasih atas pengertiannya._"
    )

    await query.edit_message_text(
      text=pesan,
      parse_mode="Markdown",
      reply_markup=tombol_menu_utama()
)
