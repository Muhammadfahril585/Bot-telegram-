# handlers/profil_pondok.py

from telegram import Update
from telegram.ext import ContextTypes
from lib.navigation import tombol_navigasi

async def handle_profil_pondok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pesan = (
        "🏫 *PROFIL PONDOK PESANTREN AL-ITQON GOWA*\n\n"
        "Pondok Pesantren Al-Itqon Gowa adalah lembaga pendidikan Islam yang berdiri sejak tahun *2019* di Kabupaten Gowa, Sulawesi Selatan. "
        "Didirikan dengan semangat untuk membina generasi Qur’ani yang berilmu, berakhlak, dan tangguh menghadapi tantangan zaman.\n\n"
        "Pondok ini memiliki fokus utama pada:\n"
        "- *Tahfizh Al-Qur’an* (menghafal dan memahami Al-Qur’an)\n"
        "- *Pendidikan formal* berbasis kurikulum nasional dan diniyah\n"
        "- *Pembinaan karakter* dan akhlakul karimah\n\n"
        "Dengan lingkungan yang islami dan tenaga pendidik profesional, Al-Itqon Gowa menjadi tempat pendidikan yang amanah dan berkualitas.\n"
        "━━━━━━━━━━━━━━━\n"
        "*Informasi Lengkap:*\n\n"
        "• *Nama Pondok*        : Al-Itqon Gowa\n"
        "• *Pimpinan*           : H. Manshur Taswin, Lc., M.Ag\n"
        "• *No. Telp Pimpinan*  : 0853-9622-4242\n"
        "• *Alamat*             : Dusun Baddo-baddo, Desa Je’nemanding\n"
        "                         Kec. Pattallassang, Kab. Gowa\n"
        "• *Didirikan*          : 01 Oktober 2019\n"
        "• *Status Tanah*       : Wakaf (luas 4000 m²)\n"
        "• *Luas Bangunan*      : 3500 m²\n"
        "• *Jumlah Santri*      : 100 Orang\n"
        "• *Jumlah Pembina*     : 12 Orang\n"
        "• *Sumber Dana*        : Infaq Santri, Donatur tetap/tidak tetap\n"
        "• *NPWP Yayasan*       : 94.065.697.8-807.000\n"
        "• *Akte Pendirian*     : No. 21 (AHU-0014658.AH.01.04.Tahun 2019)\n\n"
        "🌐 *Website*: (sedang dalam pengembangan)\n\n"
        "_Barakallahu fiikum._"
    )

    await query.edit_message_text(
        text=pesan,
        parse_mode="Markdown",
        reply_markup=tombol_navigasi("tentang")
    )
