from telegram import Update
from telegram.ext import ContextTypes
from lib.navigation import tombol_navigasi

async def handle_visi_misi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pesan = (
        "🎯 *VISI & MISI PONDOK PESANTREN AL-ITQON GOWA*\n\n"
        "*VISI:*\n"
        "🔮 Menjadi PonPes yang berlandaskan Al Qur’an dan Sunnah yang amanah, tangguh dan mandiri menuju PonPes yang diridhoi dan dicintai oleh Allah dan Rasul-Nya.\n\n"
        "*MISI:*\n"
        "Misi PPTQ AL-ITQON GOWA adalah:\n"
        "1️⃣ Menjadikan PonPes sebagai wadah beramal Jariyah.\n"
        "2️⃣ Menjadi PonPes yang Mandiri secara Financial dan Mensejahterakan Lingkungan sekitar.\n"
        "3️⃣ Berlandaskan sesuai aturan Agama dan Tradisi Ahlul Sunnah Wal Jamaah.\n"
        "4️⃣ Memberikan Kontribusi kepada Pemerintah dalam bidang Agama.\n"
        "5️⃣ Menjunjung Tinggi Adat Bugis Makassar dalam artian Siri’ na Pacce.\n"
        "6️⃣ Menjadi PonPes yang Amanah, Bertanggungjawab dan Profesional.\n\n"
        "_Pendidikan adalah investasi akhirat. Mari bersama membangun peradaban Qurani!_\n\n"
        "_Barakallahu fiikum._"
    )

    await query.edit_message_text(
       text=pesan,
       parse_mode="Markdown",
       reply_markup=tombol_navigasi("tentang")
    )
