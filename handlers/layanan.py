from telegram import Update
from telegram.ext import ContextTypes
from lib.navigation import tombol_menu_utama

async def handle_layanan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pesan = (
        "🛠️ *Layanan Pondok Al-Itqon*\n\n"
        "Berikut layanan yang tersedia:\n\n"
        "1. ✉️ *Konsultasi Santri*\n"
        "2. 📢 *Pengumuman Resmi*\n"
        "3. 📬 *Kritik & Saran*\n"
        "4. 🧾 *Permintaan Surat Resmi*\n\n"
        "_Semua layanan ini masih dalam tahap pengembangan dan akan segera tersedia melalui bot._\n\n"
        "Jika ada kebutuhan mendesak, hubungi admin: *+6285298514896* (Ustadz Laode Muh Fahril)\n\n"
        "_Barakallahu fiikum!_"
    )

    await query.edit_message_text(
      text=pesan,
      parse_mode="Markdown",
      reply_markup=tombol_menu_utama()
    )
