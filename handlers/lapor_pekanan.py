from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters
)
from lib.format_pekanan import format_laporan_pekan
from database import get_db
from datetime import datetime

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

    keyboard = [[InlineKeyboardButton(h, callback_data=f"halaqah|{h}")] for h in halaqah_list]
    await update.message.reply_text(
        "📌 Silakan pilih halaqah yang ingin dilaporkan:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return PILIH_HALAQAH

def get_santri_by_halaqah(nama_halaqah):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT s.nama FROM santri s
        JOIN halaqah h ON s.halaqah_id = h.id
        WHERE h.nama = %s
    """, (nama_halaqah,))
    results = cursor.fetchall()
    return [row[0] for row in results]

async def pilih_halaqah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    halaqah_terpilih = query.data.split("|")[1]
    context.user_data["halaqah"] = halaqah_terpilih

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT ustadz FROM halaqah WHERE nama = %s", (halaqah_terpilih,))
    result = cursor.fetchone()
    context.user_data["ustadz"] = result[0] if result else "Belum ditentukan"

    santri_list = get_santri_by_halaqah(halaqah_terpilih)
    if not santri_list:
        await query.edit_message_text("❌ Tidak ada santri dalam halaqah ini.")
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton(s, callback_data=f"santri|{s}")] for s in santri_list]
    await query.edit_message_text(
        f"✅ Halaqah terpilih: *{halaqah_terpilih}*\n\n👤 Pilih santri yang ingin dilaporkan:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    context.user_data["santri_list"] = santri_list[1:]
    context.user_data["santri"] = santri_list[0]
    return PILIH_SANTRI

async def pilih_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    santri_terpilih = query.data.split("|")[1]
    context.user_data["santri"] = santri_terpilih

    keyboard = [
        [InlineKeyboardButton("📖 Hafalan Baru", callback_data="status|hafalan_baru")],
        [InlineKeyboardButton("📚 Tahsin", callback_data="status|tahsin")],
        [InlineKeyboardButton("🔁 Muroja'ah", callback_data="status|murojaah")],
        [InlineKeyboardButton("📝 Ujian", callback_data="status|ujian")],
        [InlineKeyboardButton("📢 Sima’an", callback_data="status|simaan")],
        [InlineKeyboardButton("🤒 Sakit", callback_data="status|sakit"),
         InlineKeyboardButton("📆 Izin", callback_data="status|izin")]
    ]
    await query.edit_message_text(
        f"✅ Santri terpilih: *{santri_terpilih}*\nSilakan pilih status hafalan:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return PILIH_STATUS

async def pilih_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    status = query.data.split("|")[1]
    context.user_data["status"] = status

    if status in ["hafalan_baru", "tahsin"]:
        # Tampilkan tombol halaman 1–10
        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=f"halaman|{i}") for i in range(1, 6)],
            [InlineKeyboardButton(str(i), callback_data=f"halaman|{i}") for i in range(6, 11)]
        ]
        await query.edit_message_text(
            "📄 Pilih jumlah halaman hafalan:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return INPUT_HALAMAN

    elif status in ["murojaah", "simaan", "ujian"]:
        # Tampilkan tombol juz 1–30
        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=f"juz|{i}") for i in range(j, j + 6)]
            for j in range(1, 31, 6)
        ]
        await query.edit_message_text(
            "📘 Pilih Juz:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return INPUT_JUZ

    elif status in ["sakit", "izin"]:
        # Langsung lanjut
        nama = context.user_data["santri"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT hafalan FROM santri WHERE nama = %s", (nama,))
        result = cursor.fetchone()
        total = result[0] if result else 0

        if "santri_data" not in context.user_data:
            context.user_data["santri_data"] = []

        context.user_data["santri_data"].append({
            "nama": nama,
            "halaman": 0,
            "juz": 0,
            "status": status,
            "total_juz": total
        })
        return await lanjut_santri(update, context)

async def input_halaman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    halaman = int(query.data.split("|")[1])
    context.user_data["halaman"] = halaman

    # Setelah pilih halaman, tampilkan tombol juz
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=f"juz|{i}") for i in range(j, j + 6)]
        for j in range(1, 31, 6)
    ]
    await query.edit_message_text(
        "📘 Pilih Juz:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return INPUT_JUZ

async def input_juz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    juz = int(query.data.split("|")[1])

    nama = context.user_data["santri"]
    status = context.user_data["status"]
    halaman = context.user_data.get("halaman", 0)

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT hafalan FROM santri WHERE nama = ?", (nama,))
    result = cursor.fetchone()
    total = result[0] if result else 0

    if status == "hafalan_baru" and halaman >= 20:
        total += halaman // 20

    if "santri_data" not in context.user_data:
        context.user_data["santri_data"] = []

    context.user_data["santri_data"].append({
        "nama": nama,
        "halaman": halaman,
        "juz": juz,
        "status": status,
        "total_juz": total
    })

    return await lanjut_santri(update, context)

async def lanjut_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    santri_list = context.user_data.get("santri_list", [])

    if santri_list:
        next_santri = santri_list.pop(0)
        context.user_data["santri"] = next_santri
        context.user_data["santri_list"] = santri_list

        keyboard = [
            [InlineKeyboardButton("📖 Hafalan Baru", callback_data="status|hafalan_baru")],
            [InlineKeyboardButton("📚 Tahsin", callback_data="status|tahsin")],
            [InlineKeyboardButton("🔁 Muroja'ah", callback_data="status|murojaah")],
            [InlineKeyboardButton("📝 Ujian", callback_data="status|ujian")],
            [InlineKeyboardButton("🕌 Sima’an", callback_data="status|simaan")],
            [InlineKeyboardButton("🤒 Sakit", callback_data="status|sakit"),
             InlineKeyboardButton("📆 Izin", callback_data="status|izin")]
        ]

        text = f"✍️ Masukkan status hafalan untuk *{next_santri}*:"
        markup = InlineKeyboardMarkup(keyboard)

        if update.callback_query:
            await update.callback_query.message.reply_text(
                text, parse_mode="Markdown", reply_markup=markup
            )
        else:
            await update.message.reply_text(
                text, parse_mode="Markdown", reply_markup=markup
            )

        return PILIH_STATUS

    # Jika semua santri selesai, buat rekap dan simpan ke DB
    halaqah = context.user_data["halaqah"]
    ustadz = context.user_data["ustadz"]
    data = context.user_data["santri_data"]
    laporan = format_laporan_pekan(halaqah, ustadz, data)

    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="📄 Laporan selesai. Berikut rekap pekanannya:")
    await context.bot.send_message(chat_id=chat_id, text=laporan, parse_mode="Markdown")

    # Simpan ke database
    bulan = datetime.now().month
    pekan = (datetime.now().day - 1) // 7 + 1
    tanggal = datetime.now().strftime("%Y-%m-%d")

    db = get_db()
    cursor = db.cursor()

    for santri in data:
        cursor.execute("""
            INSERT INTO laporan_pekanan
            (nama_halaqah, nama_santri, pekan_ke, bulan, hafalan_baru, status, total_juz, tanggal_laporan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            halaqah,
            santri["nama"],
            pekan,
            bulan,
            santri["halaman"],
            santri["status"],
            santri["total_juz"],
            tanggal
        ))

    cursor.execute("""
        INSERT INTO rekap_format_awal (bulan, pekan, halaqah, ustadz, isi_laporan)
        VALUES (%s, %s, %s, %s, %s)
    """, (bulan, pekan, halaqah, ustadz, laporan))

    db.commit()
    db.close()

    return ConversationHandler.END

lapor_handler = ConversationHandler(
    entry_points=[CommandHandler("lapor", mulai_lapor)],
    states={
        PILIH_HALAQAH: [CallbackQueryHandler(pilih_halaqah, pattern=r"^halaqah\|")],
        PILIH_SANTRI: [CallbackQueryHandler(pilih_santri, pattern=r"^santri\|")],
        PILIH_STATUS: [CallbackQueryHandler(pilih_status, pattern=r"^status\|")],
        INPUT_HALAMAN: [CallbackQueryHandler(input_halaman, pattern=r"^halaman\|")],
        INPUT_JUZ: [CallbackQueryHandler(input_juz, pattern=r"^juz\|")],
    },
    fallbacks=[]
)
