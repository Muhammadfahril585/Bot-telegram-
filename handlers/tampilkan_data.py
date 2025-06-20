from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from database import get_db

ADMIN_IDS = {970201320}  # Ganti dengan user_id Telegram admin kamu

# State
PILIHAN, LIHAT_PER_KELAS, LIHAT_PER_JENJANG, LIHAT_PER_NAMA, LIHAT_PER_ANGKATAN = range(5)

# Inline keyboard buttons
inline_keyboard = [
    [
        InlineKeyboardButton("📚Lihat Semua", callback_data="lihat_semua"),
        InlineKeyboardButton("⛺️Lihat Per Kelas", callback_data="lihat_per_kelas"),
    ],
    [
        InlineKeyboardButton("🛖Lihat Per Jenjang", callback_data="lihat_per_jenjang"),
        InlineKeyboardButton("📆Lihat Per Angkatan", callback_data="lihat_per_angkatan"),
    ],
    [
        InlineKeyboardButton("👥Lihat Daftar Nama", callback_data="lihat_nama"),
        InlineKeyboardButton("🎓Lihat Alumni", callback_data="lihat_daftar_alumni"),
    ]
]
markup = InlineKeyboardMarkup(inline_keyboard)

async def mulai_lihat_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Maaf🙏, fitur ini hanya untuk admin.")
        return ConversationHandler.END
    await update.message.reply_text("🫴Silakan pilih cara menampilkan data santri:", reply_markup=markup)
    return PILIHAN

async def proses_pilihan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Maaf🙏, fitur ini hanya untuk admin.")
        return ConversationHandler.END
    query = update.callback_query
    await query.answer()
    pilihan = query.data

    conn = get_db()
    c = conn.cursor()

    if pilihan == "lihat_semua":
        c.execute("SELECT nama_lengkap FROM santri_nama ORDER BY nama_lengkap")
        daftar_aktif = c.fetchall()

        c.execute("SELECT COUNT(*) FROM alumni")
        jumlah_alumni = c.fetchone()[0]

        total_aktif = len(daftar_aktif)
        teks = f"📚 Daftar Semua Santri (Aktif: {total_aktif}) (Alumni: {jumlah_alumni}):\n\n"
        for i, (nama,) in enumerate(daftar_aktif, 1):
            teks += f"{i}. {nama}\n"

        await query.edit_message_text(teks, parse_mode="Markdown")
        return ConversationHandler.END

    elif pilihan == "lihat_per_kelas":
        await query.edit_message_text("‼️Masukkan jenjang dan kelas (contoh: SMP 1 atau SMA 3):")
        return LIHAT_PER_KELAS

    elif pilihan == "lihat_per_jenjang":
        await query.edit_message_text("‼️Masukkan jenjang saja (contoh: SMP atau SMA):")
        return LIHAT_PER_JENJANG

    elif pilihan == "lihat_per_angkatan":
        await query.edit_message_text("🫴Silakan ketik tahun angkatan (contoh: 2023):")
        return LIHAT_PER_ANGKATAN

    elif pilihan == "lihat_nama":
        return await proses_nama(update, context)

    else:
        await query.edit_message_text("Pilihan tidak dikenali.")
        return ConversationHandler.END

async def proses_kelas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Maaf🙏, fitur ini hanya untuk admin.")
        return ConversationHandler.END

    text = update.message.text.strip().upper()
    parts = text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await update.message.reply_text("❌Format salah. Contoh yang benar: SMP 1 atau SMA 3.")
        return ConversationHandler.END

    jenjang, tingkat = parts[0], int(parts[1])
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT sn.nama_lengkap
        FROM kelas k
        JOIN santri_nama sn ON k.santri_nama_id = sn.id
        WHERE k.jenjang = %s AND k.tingkat = %s
        ORDER BY sn.nama_lengkap
    """, (jenjang, tingkat))
    hasil = c.fetchall()
    jumlah = len(hasil)
    if hasil:
        pesan = f"📋Daftar Santri Kelas {jenjang} {tingkat}:\n"
        for i, (nama,) in enumerate(hasil, 1):
            pesan += f"{i}. {nama}\n"
    else:
        pesan = f"⚠️Tidak ada santri di kelas {jenjang} {tingkat}."
    await update.message.reply_text(pesan, parse_mode="Markdown")
    return ConversationHandler.END

async def proses_angkatan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Maaf🙏, fitur ini hanya untuk admin.")
        return ConversationHandler.END
    angkatan = int(update.message.text.strip())

    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT sn.nama_lengkap
        FROM angkatan a
        JOIN santri_nama sn ON a.santri_nama_id = sn.id
        WHERE a.angkatan = %s
    """, (angkatan,))
    hasil = c.fetchall()
    jumlah = len(hasil)
    if hasil:
        pesan = f"📋 Daftar Santri Angkatan {angkatan} ({jumlah} santri):\n"
        for i, (nama,) in enumerate(hasil, 1):
            pesan += f"{i}. {nama}\n"
        await update.message.reply_text(pesan, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Tidak ada santri di angkatan {angkatan}.")
    return ConversationHandler.END

async def proses_nama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, nama_lengkap FROM santri_nama ORDER BY nama_lengkap ASC")
    data = c.fetchall()

    if not data:
        await query.edit_message_text("Belum ada data santri.")
        return ConversationHandler.END

    keyboard = []
    for santri_id, nama in data:
        keyboard.append([InlineKeyboardButton(nama, callback_data=f"lihat_santri_{santri_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📌Pilih nama santri untuk melihat detail:", reply_markup=reply_markup)
    return ConversationHandler.END

async def callback_nama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    santri_id = int(query.data.split("_")[-1])

    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT
            sn.nama_lengkap, s.nis, s.nik, s.nomor_kk, s.tempat_lahir, s.tanggal_lahir,
            s.jenis_kelamin, s.agama, s.anak_ke, s.provinsi, s.kabupaten, s.kecamatan, s.alamat, k.jenjang, k.tingkat,
            p.nama_lembaga, p.npns, p.jenis_pendidikan, p.lokasi_lembaga, p.provinsi, p.tahun_lulus,
            w.ayah_nama, w.ayah_tempat_lahir, w.ayah_tanggal_lahir, w.ayah_nik, w.ayah_pendidikan, w.ayah_pekerjaan,
            w.ibu_nama, w.ibu_tempat_lahir, w.ibu_tanggal_lahir, w.ibu_nik, w.ibu_pendidikan, w.ibu_pekerjaan
        FROM santri_nama sn
        LEFT JOIN santri_data_pribadi s ON sn.id = s.santri_nama_id
        LEFT JOIN pendidikan p ON sn.id = p.santri_nama_id
        LEFT JOIN wali w ON sn.id = w.santri_nama_id
        LEFT JOIN kelas k ON sn.id = k.santri_nama_id
        WHERE sn.id = %s
        LIMIT 1
    """, (santri_id,))
    data = c.fetchone()
    if not data:
        await query.edit_message_text("Data santri tidak ditemukan.")
        return ConversationHandler.END

    (
        nama, nis, nik, nomor_kk, tempat, tgl, jk, agama, anak_ke, provinsi, kabupaten, kecamatan, alamat, jenjang, tingkat,
        sekolah_nama, sekolah_npns, sekolah_jenis, sekolah_lokasi, sekolah_prov, sekolah_lulus,
        ayah_nama, ayah_tmp, ayah_tgl, ayah_nik, ayah_pdk, ayah_job,
        ibu_nama, ibu_tmp, ibu_tgl, ibu_nik, ibu_pdk, ibu_job
    ) = data

    pesan = f"""👤Nama: {nama}

NIS: {nis}
NIK: {nik}
NO.KK: {nomor_kk}
TTL: {tempat}, {tgl}
Jenis Kelamin: {jk}
Agama: {agama}
Anak ke: {anak_ke}
Alamat: {alamat}
Kecamatan: {kecamatan}
Kabupaten: {kabupaten}
Provinsi: {provinsi}
Kelas Saat Ini: {jenjang} {tingkat}

🏫Sekolah Asal:
Nama: {sekolah_nama}
NPNS: {sekolah_npns}
Lokasi: {sekolah_lokasi}
Tahun Lulus: {sekolah_lulus}
Provinsi: {sekolah_prov}

👱‍♂Ayah:
Nama: {ayah_nama}
TTL: {ayah_tmp}, {ayah_tgl}
NIK: {ayah_nik}
Pendidikan: {ayah_pdk}
Pekerjaan: {ayah_job}

👩‍🦰Ibu:
Nama: {ibu_nama}
TTL: {ibu_tmp}, {ibu_tgl}
NIK: {ibu_nik}
Pendidikan: {ibu_pdk}
Pekerjaan: {ibu_job}"""
    await query.edit_message_text(pesan, parse_mode="Markdown")
    return ConversationHandler.END

async def proses_jenjang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jenjang = update.message.text.strip().upper()
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT sn.nama_lengkap, k.tingkat
        FROM kelas k
        JOIN santri_nama sn ON k.santri_nama_id = sn.id
        WHERE k.jenjang = %s
        ORDER BY k.tingkat, sn.nama_lengkap
    """, (jenjang,))
    hasil = c.fetchall()

    if hasil:
        pesan = f"📋Daftar Santri Jenjang {jenjang}:\n"
        for i, (nama, tingkat) in enumerate(hasil, 1):
            pesan += f"{i}. {nama} (Kelas {tingkat})\n"
    else:
        pesan = f"❌Tidak ada santri di jenjang {jenjang}."

    await update.message.reply_text(pesan, parse_mode="Markdown")
    return ConversationHandler.END

# Handler untuk dispatcher
lihat_data_handler = ConversationHandler(
    entry_points=[CommandHandler("lihat_santri", mulai_lihat_data)],
    states={
        PILIHAN: [CallbackQueryHandler(proses_pilihan)],
        LIHAT_PER_KELAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_kelas)],
        LIHAT_PER_JENJANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_jenjang)],
        LIHAT_PER_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_nama)],
        LIHAT_PER_ANGKATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_angkatan)],
    },
    fallbacks=[CommandHandler("lihat_santri", mulai_lihat_data)],
    )
