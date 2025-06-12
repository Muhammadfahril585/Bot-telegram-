from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler
from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from lib.format_pekanan import format_laporan_pekan
from database import get_db


PILIH_HALAQAH, PILIH_SANTRI, PILIH_STATUS, INPUT_HALAMAN, INPUT_JUZ = range(5)

def get_halaqah_list():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT nama FROM halaqah")
    results = cursor.fetchall()
    return [row[0] for row in results]
async def mulai_lapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    halaqah_list = get_halaqah_list()
    if not halaqah_list:
        await update.message.reply_text("❌ Belum ada halaqah yang terdaftar.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton(h, callback_data=f"halaqah|{h}")]
        for h in halaqah_list
    ]
    await update.message.reply_text(
        "📌 Silakan pilih halaqah yang ingin dilaporkan:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return PILIH_HALAQAH

def get_santri_by_halaqah(nama_halaqah):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT s.nama 
        FROM santri s 
        JOIN halaqah h ON s.halaqah_id = h.id 
        WHERE h.nama = ?
    """, (nama_halaqah,))
    results = cursor.fetchall()
    return [row[0] for row in results]

async def pilih_halaqah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    halaqah_terpilih = query.data.split("|")[1]
    context.user_data["halaqah"] = halaqah_terpilih

# 🔍 Ambil nama ustadz dari tabel halaqah
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT ustadz FROM halaqah WHERE nama = ?", (halaqah_terpilih,))
    result = cursor.fetchone()
    context.user_data["ustadz"] = result[0] if result else "Belum ditentukan"
    santri_list = get_santri_by_halaqah(halaqah_terpilih)
    if not santri_list:
        await query.edit_message_text("❌ Tidak ada santri dalam halaqah ini.")
        return ConversationHandler.END
    keyboard = [
        [InlineKeyboardButton(s, callback_data=f"santri|{s}")] for s in santri_list
    ]
    await query.edit_message_text(
        f"✅ Halaqah terpilih: *{halaqah_terpilih}*\n\n👤 Pilih santri yang ingin dilaporkan:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    context.user_data["santri_list"] = santri_list[1:]  # sisakan yang pertama
    context.user_data["santri"] = santri_list[0]  # mulai dari santri pertama
    return PILIH_SANTRI

async def pilih_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    santri_terpilih = query.data.split("|")[1]
    context.user_data["santri"] = santri_terpilih
    keyboard = [
        [InlineKeyboardButton("📖 Hafalan Baru", callback_data="status|hafalan_baru")],
        [InlineKeyboardButton("🔁 Muroja'ah", callback_data="status|murojaah")],
        [InlineKeyboardButton("📝 Ujian", callback_data="status|ujian")],
        [InlineKeyboardButton("🕌 Sima’an", callback_data="status|simaan")],
        [InlineKeyboardButton("🤒 Sakit", callback_data="status|sakit"), InlineKeyboardButton("📆 Izin", callback_data="status|izin")],
    ]
    await query.edit_message_text(
        f"✅ Santri terpilih: *{santri_terpilih}*\n"
        f"Silakan pilih status hafalan di bawah ini:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return PILIH_STATUS

async def pilih_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    status_terpilih = query.data.split("|")[1]
    context.user_data["status"] = status_terpilih

    if status_terpilih == "hafalan_baru":
        await query.edit_message_text("📘 Masukkan jumlah halaman yang dihafal:")
        return INPUT_HALAMAN

    elif status_terpilih in ["murojaah", "ujian", "simaan"]:
        teks = {
            "murojaah": "🔁 Masukkan juz yang di-muroja'ah:",
            "ujian": "📝 Masukkan juz ujian:",
            "simaan": "🕌 Masukkan jumlah juz yang akan disima’an:"
        }
        await query.edit_message_text(teks[status_terpilih])
        return INPUT_JUZ

    elif status_terpilih in ["sakit", "izin"]:
        # Ambil info
        halaqah = context.user_data.get("halaqah")
        ustadz = context.user_data.get("ustadz")
        santri = context.user_data.get("santri")

        # Ambil hafalan total dari database
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT hafalan FROM santri WHERE nama = ?", (santri,))
        result = cursor.fetchone()
        total_hafalan = result[0] if result else 0

        # Simpan ke list santri_data
        if "santri_data" not in context.user_data:
            context.user_data["santri_data"] = []

        context.user_data["santri_data"].append({
            "nama": santri,
            "status": status_terpilih,
            "halaman": 0,
            "juz": 0,
            "total_juz": total_hafalan
        })

        # Lanjutkan ke santri berikutnya
        santri_list = context.user_data.get("santri_list", [])
        if santri_list:
            santri_selanjutnya = santri_list.pop(0)
            context.user_data["santri"] = santri_selanjutnya
            context.user_data["santri_list"] = santri_list

            # Tampilkan lagi pilihan status
            keyboard = [
                [
                    InlineKeyboardButton("📖 Hafalan Baru", callback_data="status|hafalan_baru"),
                    InlineKeyboardButton("🔁 Murojaah", callback_data="status|murojaah"),
                ],
                [
                    InlineKeyboardButton("📝 Ujian", callback_data="status|ujian"),
                    InlineKeyboardButton("🕌 Simaan", callback_data="status|simaan"),
                ],
                [
                    InlineKeyboardButton("🤒 Sakit", callback_data="status|sakit"),
                    InlineKeyboardButton("📌 Izin", callback_data="status|izin"),
                ]
            ]
            await query.edit_message_text(
                f"✍️ Masukkan status hafalan untuk *{santri_selanjutnya}*:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return PILIH_STATUS

        # Jika sudah tidak ada santri tersisa, tampilkan rekap
        from lib.format_pekanan import format_laporan_pekan
        laporan = format_laporan_pekan(halaqah, ustadz, context.user_data["santri_data"])

        await query.edit_message_text(
            f"✅ Laporan untuk *{santri}* di halaqah *{halaqah}* dengan status *{status_terpilih.capitalize()}* telah disimpan.\n\n{laporan}",
            parse_mode="Markdown"
        )

        # SIMPAN KE DATABASE
        from datetime import datetime
        tanggal = datetime.now().strftime("%Y-%m-%d")
        bulan = datetime.now().strftime("%B")
        pekan = (datetime.now().day - 1) // 7 + 1

        for data in context.user_data["santri_data"]:
            cursor.execute("""
                INSERT INTO laporan_pekanan 
                (nama_halaqah, nama_santri, pekan_ke, bulan, hafalan_baru, status, total_juz, tanggal_laporan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                halaqah, data["nama"], pekan, bulan, data["halaman"],
                data["status"], data["total_juz"], tanggal
            ))

        cursor.execute("""
            INSERT INTO rekap_format_awal (bulan, pekan, halaqah, ustadz, isi_laporan)
            VALUES (?, ?, ?, ?, ?)
        """, (datetime.now().month, pekan, halaqah, ustadz, laporan))

        db.commit()

        return ConversationHandler.END
async def input_halaman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        halaman = int(update.message.text.strip())
        if halaman < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Harap masukkan angka halaman yang valid.")
        return INPUT_HALAMAN

    context.user_data["halaman"] = halaman
    await update.message.reply_text("📘 Masukkan Juz ke-berapa:")
    return INPUT_JUZ

async def input_juz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        juz = int(update.message.text.strip())
        if juz <= 0 or juz > 30:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Harap masukkan angka juz yang valid (1-30).")
        return INPUT_JUZ

    nama_santri = context.user_data["santri"]
    halaman = context.user_data.get("halaman", 0)
    status_input = context.user_data.get("status", "hafalan_baru")

    # Ambil hafalan total dari database
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT hafalan FROM santri WHERE nama = ?", (nama_santri,))
    result = cursor.fetchone()
    total_hafalan = result[0] if result else 0

    # Tambah total hafalan jika ada hafalan baru dan mencapai 20 halaman
    if status_input == "hafalan_baru" and halaman >= 20:
        total_hafalan += halaman // 20

    # Simpan data ke context
    if "santri_data" not in context.user_data:
        context.user_data["santri_data"] = []

    context.user_data["santri_data"].append({
        "nama": nama_santri,
        "status": status_input,
        "halaman": halaman,
        "juz": juz,
        "total_juz": total_hafalan
    })

    # Reset halaman agar tidak terbawa ke santri berikutnya
    context.user_data["halaman"] = 0

    # Ambil santri berikutnya
    santri_list = context.user_data.get("santri_list", [])
    if santri_list:
        santri_selanjutnya = santri_list.pop(0)
        context.user_data["santri"] = santri_selanjutnya
        context.user_data["santri_list"] = santri_list

        # Tampilkan pilihan status untuk santri berikutnya
        keyboard = [
            [
                InlineKeyboardButton("📖 Hafalan Baru", callback_data="status|hafalan_baru"),
                InlineKeyboardButton("🔁 Murojaah", callback_data="status|murojaah"),
            ],
            [
                InlineKeyboardButton("📝 Ujian", callback_data="status|ujian"),
                InlineKeyboardButton("🕌 Simaan", callback_data="status|simaan"),
            ],
            [
                InlineKeyboardButton("🤒 Sakit", callback_data="status|sakit"),
                InlineKeyboardButton("📌 Izin", callback_data="status|izin"),
            ]
        ]
        await update.message.reply_text(
            f"✍️ Masukkan status hafalan untuk *{santri_selanjutnya}*:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return PILIH_STATUS

    # Jika tidak ada santri lagi
    halaqah = context.user_data.get("halaqah", "Tidak Diketahui")
    ustadz = context.user_data.get("ustadz", "Tidak Diketahui")
    santri_data = context.user_data["santri_data"]

    from lib.format_pekanan import format_laporan_pekan
    laporan = format_laporan_pekan(halaqah, ustadz, santri_data)

    # Kirim rekap
    await update.message.reply_text("📄 Laporan selesai. Berikut rekap pekanannya:")
    await update.message.reply_text(laporan, parse_mode="Markdown")

    # ⬇️ SIMPAN KE DATABASE
    from datetime import datetime
    bulan = datetime.now().strftime("%B")
    pekan = (datetime.now().day - 1) // 7 + 1
    tanggal = datetime.now().strftime("%Y-%m-%d")

    # Simpan ke laporan_pekanan
    for santri in santri_data:
        cursor.execute("""
            INSERT INTO laporan_pekanan 
            (nama_halaqah, nama_santri, pekan_ke, bulan, hafalan_baru, status, total_juz, tanggal_laporan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            halaqah,
            santri["nama"],
            pekan,
            bulan,
            santri.get("halaman", 0),
            santri["status"],
            santri.get("total_juz", 0),
            tanggal
        ))

    # Simpan ke rekap_format_awal
    cursor.execute("""
        INSERT INTO rekap_format_awal (bulan, pekan, halaqah, ustadz, isi_laporan)
        VALUES (?, ?, ?, ?, ?)
    """, (
        pekan,  # bulan disimpan sebagai integer atau teks tergantung struktur
        pekan,
        halaqah,
        ustadz,
        laporan
    ))

    db.commit()
    db.close()

    return ConversationHandler.END
lapor_handler = ConversationHandler(
    entry_points=[CommandHandler("lapor", mulai_lapor)],
    states={
        PILIH_HALAQAH: [CallbackQueryHandler(pilih_halaqah, pattern=r"^halaqah\|")],
        PILIH_SANTRI: [CallbackQueryHandler(pilih_santri, pattern=r"^santri\|")],
        PILIH_STATUS: [CallbackQueryHandler(pilih_status, pattern=r"^status\|")],
        INPUT_HALAMAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_halaman)],
        INPUT_JUZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_juz)],
    },
    fallbacks=[]
)
