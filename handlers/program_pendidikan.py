from telegram import Update
from telegram.ext import ContextTypes
from lib.navigation import tombol_menu_utama

async def handle_program_pendidikan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pesan = (
        "🎓 *PROGRAM PENDIDIKAN PONDOK PESANTREN AL-ITQON GOWA*\n\n"
        "Pondok kami menyelenggarakan beberapa jenjang dan program utama:\n\n"
        "1. *Raudatul Athfal (RA)*\n"
        "   Pendidikan anak usia dini yang mengintegrasikan kurikulum umum dan agama.\n\n"
        "2. *Madrasah Tsanawiyah (MTs)*\n"
        "   Jenjang menengah pertama yang fokus pada pembentukan karakter dan pendalaman ilmu syar'i.\n\n"
        "3. *Madrasah Aliyah (MA)*\n"
        "   Tingkat menengah atas, menyiapkan santri untuk jenjang perguruan tinggi dengan pondasi ilmu agama yang kuat.\n\n"
        "4. *Program Tahfizh Al-Qur'an*\n"
        "   Target utama: Hafal 30 juz selama masa pendidikan.\n\n"
        "5. *Kelas Khusus Bahasa Arab dan Inggris*\n"
        "   Mendukung santri dalam penguasaan bahasa asing sebagai bekal dakwah global.\n\n"
        "6. *Ekstrakurikuler*\n"
        "   Bekerja sama, olahraga, seni bela diri, komputer, dan kegiatan lainnya.\n\n"
        "Dengan visi membentuk generasi Qur’ani yang berakhlakul karimah, seluruh program pendidikan disusun untuk mendukung tujuan tersebut.\n\n"
        "_Barakallahu fiikum._"
    )

    await query.edit_message_text(
        text=pesan,
        parse_mode="Markdown",
        reply_markup=tombol_menu_utama()
    )
