from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from utils.gsheet import get_sheet
import datetime
import asyncio
import telegram  # untuk telegram.error.BadRequest

# ================== KONFIGURASI ==================
NAMA_SHEET = "DATA_SANTRI"
JUMLAH_PER_HALAMAN = 10

# Daftar ID yang diizinkan (diambil dari lapor_pekanan2.py)
ALLOWED_IDS = {
    970201320, 124440394, 5444585835, 6390533939, 7637004025, 7496056677, 6476932444, 8122376813, 6194307035, 1081341314, 8354592920
}

# State conversation
PILIH_MODE, CARI_NIK, CARI_NAMA = range(3) # INPUT_PASSWORD dihapus
# =================================================

def get_data_santri():
    sheet = get_sheet(NAMA_SHEET)
    # Ambil dari baris ke-3 ke bawah (sesuai kode awal)
    return sheet.get_all_values()[2:]

# ====== STEP 1: cek akses ID ======
async def minta_akses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_IDS:
        await update.message.reply_text("❌ Anda tidak memiliki akses ke fitur data santri.")
        return ConversationHandler.END

    context.user_data["verified_data_santri"] = True
    return await start_data_santri_menu(update, context, is_callback=False)
    
async def admin_entry_data_santri(update, context):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    if user_id not in ALLOWED_IDS:
        await q.answer("❌ Anda tidak memiliki akses.", show_alert=True)
        return ConversationHandler.END

    context.user_data["verified_data_santri"] = True
    await q.message.reply_text("✅ Akses diverifikasi.")
    return await start_data_santri_menu(update, context, is_callback=True)

async def start_data_santri_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool):
    keyboard = [
        [InlineKeyboardButton("🔍 Cari Berdasarkan NIK", callback_data="mode|nik")],
        [InlineKeyboardButton("🔍 Cari Berdasarkan Nama", callback_data="mode|nama_partial")],
        [InlineKeyboardButton("📑 Lihat Daftar Nama Santri", callback_data="mode|nama")]
    ]
    
    message_source = update.callback_query.message if is_callback and update.callback_query else update.message
    
    await message_source.reply_text(
        "✅ Berhasil! \n\n📋 *Pilih Mode Pencarian Data Santri:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return PILIH_MODE
# =========================================

async def pilih_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Pastikan sudah verifikasi
    if not context.user_data.get("verified_data_santri"):
        await query.edit_message_text("🔒 Akses dikunci. Silakan mulai ulang perintah.")
        return ConversationHandler.END

    mode = query.data.split("|")[1]
    context.user_data["santri_data"] = get_data_santri()

    if mode == "nik":
        await query.edit_message_text(
            text="✍️ Silakan *masukkan NIK* santri yang ingin dicari:",
            parse_mode='Markdown'
        )
        return CARI_NIK
    elif mode == "nama_partial":
        await query.edit_message_text(
            text="✍️ Silakan *masukkan nama* santri yang ingin dicari (bisa sebagian nama):",
            parse_mode='Markdown'
        )
        return CARI_NAMA
    elif mode == "nama":
        context.user_data["halaman"] = 0
        await tampilkan_nama_inline(query, context)
        return PILIH_MODE

async def proses_cari_nik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_data_santri"):
        await update.message.reply_text("🔒 Akses dikunci. Silakan mulai ulang perintah.")
        return ConversationHandler.END

    nik_input = update.message.text.strip()
    data = context.user_data.get("santri_data", get_data_santri())

    for row in data:
        if len(row) > 1 and row[1] == nik_input:
            return await tampilkan_detail(row, update)

    await update.message.reply_text("❌ Data tidak ditemukan untuk NIK tersebut.")
    return ConversationHandler.END

async def proses_cari_nama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_data_santri"):
        await update.message.reply_text("🔒 Akses dikunci. Silakan mulai ulang perintah.")
        return ConversationHandler.END

    nama_input = update.message.text.strip().lower()
    context.user_data["kata_kunci_pencarian"] = nama_input # Simpan kata kunci untuk ditampilkan
    data = context.user_data.get("santri_data", get_data_santri())

    # Cari nama yang mengandung kata kunci (case insensitive)
    hasil_pencarian = []
    for row in data:
        if len(row) > 2 and nama_input in row[2].lower():
            hasil_pencarian.append(row)

    if not hasil_pencarian:
        await update.message.reply_text("❌ Tidak ditemukan santri dengan nama yang mengandung kata kunci tersebut.")
        return ConversationHandler.END

    # Simpan hasil pencarian untuk navigasi
    context.user_data["hasil_pencarian_nama"] = hasil_pencarian
    context.user_data["halaman_pencarian"] = 0

    await tampilkan_hasil_pencarian_nama(update, context)
    return PILIH_MODE

async def tampilkan_hasil_pencarian_nama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hasil_pencarian = context.user_data.get("hasil_pencarian_nama", [])
    halaman = context.user_data.get("halaman_pencarian", 0)
    awal = halaman * JUMLAH_PER_HALAMAN
    akhir = awal + JUMLAH_PER_HALAMAN
    potongan = hasil_pencarian[awal:akhir]

    keyboard = [
        [InlineKeyboardButton(f"{i+1+awal}. {row[2] if len(row)>2 else 'Tanpa Nama'}", callback_data=f"lihat|{row[2] if len(row)>2 else ''}")]
        for i, row in enumerate(potongan)
    ]

    navigasi = []
    if halaman > 0:
        navigasi.append(InlineKeyboardButton("⬅️ Sebelumnya", callback_data="navi_pencarian|prev"))
    if akhir < len(hasil_pencarian):
        navigasi.append(InlineKeyboardButton("➡️ Selanjutnya", callback_data="navi_pencarian|next"))

    if navigasi:
        keyboard.append(navigasi)

    # Tambahkan tombol kembali ke menu pencarian
    keyboard.append([InlineKeyboardButton("🔙 Kembali ke Menu Pencarian", callback_data="kembali_ke_menu")])

    if isinstance(update, Update) and update.message:
        await update.message.reply_text(
            text=f"🔍 *Hasil Pencarian untuk '{context.user_data.get('kata_kunci_pencarian', '')}':* ({len(hasil_pencarian)} hasil ditemukan)",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        # Menghandle edit_message_text jika berasal dari callback
        try:
            await update.edit_message_text(
                text=f"🔍 *Hasil Pencarian untuk '{context.user_data.get('kata_kunci_pencarian', '')}':* ({len(hasil_pencarian)} hasil ditemukan)",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        except telegram.error.BadRequest as e:
            if "Message is not modified" in str(e):
                pass
            else:
                raise

async def navigasi_pencarian_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("verified_data_santri"):
        await query.edit_message_text("🔒 Akses dikunci. Silakan mulai ulang perintah.")
        return ConversationHandler.END

    arah = query.data.split("|")[1]

    if arah == "next":
        context.user_data["halaman_pencarian"] += 1
    elif arah == "prev" and context.user_data["halaman_pencarian"] > 0:
        context.user_data["halaman_pencarian"] -= 1

    await tampilkan_hasil_pencarian_nama(query, context)

async def kembali_ke_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("verified_data_santri"):
        await query.edit_message_text("🔒 Akses dikunci. Silakan mulai ulang perintah.")
        return ConversationHandler.END

    # Hapus data pencarian
    if "hasil_pencarian_nama" in context.user_data:
        del context.user_data["hasil_pencarian_nama"]
    if "halaman_pencarian" in context.user_data:
        del context.user_data["halaman_pencarian"]
    if "kata_kunci_pencarian" in context.user_data:
        del context.user_data["kata_kunci_pencarian"]
    if "halaman" in context.user_data:
        del context.user_data["halaman"]

    # Tampilkan menu mode pencarian lagi
    keyboard = [
        [InlineKeyboardButton("🔍 Cari Berdasarkan NIK", callback_data="mode|nik")],
        [InlineKeyboardButton("🔍 Cari Berdasarkan Nama", callback_data="mode|nama_partial")],
        [InlineKeyboardButton("📑 Lihat Daftar Nama Santri", callback_data="mode|nama")]
    ]
    await query.edit_message_text(
        "📋 *Pilih Mode Pencarian Data Santri:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return PILIH_MODE

async def tampilkan_nama_inline(query, context):
    data = context.user_data["santri_data"]
    halaman = context.user_data["halaman"]
    awal = halaman * JUMLAH_PER_HALAMAN
    akhir = awal + JUMLAH_PER_HALAMAN
    potongan = data[awal:akhir]

    keyboard = [
        [InlineKeyboardButton(f"{i+1+awal}. {row[2] if len(row)>2 else 'Tanpa Nama'}", callback_data=f"lihat|{row[2] if len(row)>2 else ''}")]
        for i, row in enumerate(potongan)
    ]

    navigasi = []
    if halaman > 0:
        navigasi.append(InlineKeyboardButton("⬅️ Sebelumnya", callback_data="navi|prev"))
    if akhir < len(data):
        navigasi.append(InlineKeyboardButton("➡️ Selanjutnya", callback_data="navi|next"))

    if navigasi:
        keyboard.append(navigasi)
        
    # Tambahkan tombol kembali ke menu pencarian
    keyboard.append([InlineKeyboardButton("🔙 Kembali ke Menu Pencarian", callback_data="kembali_ke_menu")])

    try:
        await query.edit_message_text(
            text="📋 *Pilih Nama Santri:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except telegram.error.BadRequest as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

async def navigasi_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("verified_data_santri"):
        await query.edit_message_text("🔒 Akses dikunci. Silakan mulai ulang perintah.")
        return ConversationHandler.END

    arah = query.data.split("|")[1]

    if arah == "next":
        context.user_data["halaman"] += 1
    elif arah == "prev" and context.user_data["halaman"] > 0:
        context.user_data["halaman"] -= 1

    await tampilkan_nama_inline(query, context)

async def tampilkan_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("verified_data_santri"):
        await query.edit_message_text("🔒 Akses dikunci. Silakan mulai ulang perintah.")
        return ConversationHandler.END

    chat_id = query.message.chat.id
    message_id = query.message.message_id

    # Tampilkan loading
    try:
        await query.edit_message_text(text="🔄 Membuka detail...", reply_markup=None)
    except telegram.error.BadRequest:
        pass  # Abaikan jika isi pesan tidak berubah

    nama = query.data.split("|")[1]
    data = context.user_data.get("santri_data", get_data_santri())

    for row in data:
        if len(row) > 2 and row[2] == nama:
            await asyncio.sleep(0.5)
            await tampilkan_detail(row, query)
            # Hapus pesan loading
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass
            return ConversationHandler.END

    await query.message.reply_text("Santri tidak ditemukan.")
    return ConversationHandler.END

async def tampilkan_detail(row, msg_or_query):
    # Defensive unpacking agar aman jika kolom kurang
    (nis, nik, nama, tmp_lahir, tgl_lahir, jk, agama, anak_ke, alamat, kecamatan, kabupaten, provinsi, sekolah, 
     jenis, npsn, lokasi, lulus, provinsi_sekolah, ayah, kk, nikayah, t4ayah, tgl_lahirayah, pendidikan, job, ibu, 
     nikibu, t4ibu, tglibu, pndibu, pkibu, status, file_id) = (row + [''] * 33)[:33]

    try:
        tgl_lahir = datetime.datetime.strptime(tgl_lahir, "%d/%m/%Y").strftime("%d-%m-%Y")
    except:
        pass

    file_id = row[32].strip() if len(row) > 32 else None
    msg = (
        f"*📄 Detail Santri:*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Nama:* {nama}\n"
        f"🆔 *NIS:* `{nis}`\n"
        f"🪪 *NIK:* `{nik}`\n"
        f"🎂 *Tempat, Tanggal Lahir:* {tmp_lahir}, {tgl_lahir}\n"
        f"🚻 *Jenis Kelamin:* {jk}\n"
        f"🕌 *Agama:* {agama}\n"
        f"👶 *Anak ke:* {anak_ke}\n"
        f"📍 *Alamat:* {alamat}\n"
        f"🗺️  *Kecamatan:* {kecamatan}\n"
        f"🏙️  *Kabupaten:* {kabupaten}\n"
        f"🏜️  *Provinsi:* {provinsi}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"*📄 Data Pendidikan:*\n"
        f"🏫 *Nama:* {sekolah}\n"
        f"🏭 *Jenis Pendidikan:* {jenis}\n"
        f"🧾 *NPSN:* `{npsn}`\n"
        f"📍 *Lokasi:* {lokasi}\n"
        f"🗓 *Tahun Lulus:* {lulus}\n"
        f"🏞 *Provinsi:* {provinsi_sekolah}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"*📑 Data Orangtua/Wali:*\n"
        f"👨‍🦰*Nama Ayah:* {ayah}\n"
        f"📋 *Nomor KK:* {kk}\n"
        f"🗂  *NIK :* {nikayah}\n"
        f"🎂 *Tempat, Tanggal Lahir:* {t4ayah}, {tgl_lahirayah}\n"
        f"📚 *Pendidikan:* {pendidikan}\n"
        f"🔨 *Pekerjaan:* {job}\n"
        f"🧕🏻*Nama Ibu:* {ibu}\n"
        f"🗂  *NIK :* {nikibu}\n"
        f"🎂 *Tempat, Tanggal Lahir:* {t4ibu}, {tglibu}\n"
        f"📚 *Pendidikan:* {pndibu}\n"
        f"🔨 *Pekerjaan:* {pkibu}"
    )

    if file_id and len(file_id) > 50:
        try:
            # Pengecekan apakah input adalah Update (dari Message) atau CallbackQuery
            if isinstance(msg_or_query, Update):
                await msg_or_query.message.reply_photo(
                    photo=file_id,
                    caption=msg,
                    parse_mode="Markdown"
                )
            else: # Asumsikan CallbackQuery
                await msg_or_query.message.reply_photo(
                    photo=file_id,
                    caption=msg,
                    parse_mode="Markdown"
                )
        except Exception as e:
            # Pengecekan apakah input adalah Update (dari Message) atau CallbackQuery
            if isinstance(msg_or_query, Update):
                await msg_or_query.message.reply_text(
                    f"⚠️ Gagal menampilkan foto:\n{e}\n\n{msg}",
                    parse_mode="Markdown"
                )
            else: # Asumsikan CallbackQuery
                await msg_or_query.message.reply_text(
                    f"⚠️ Gagal menampilkan foto:\n{e}\n\n{msg}",
                    parse_mode="Markdown"
                )
    else:
        # Pengecekan apakah input adalah Update (dari Message) atau CallbackQuery
        if isinstance(msg_or_query, Update):
            await msg_or_query.message.reply_text(msg, parse_mode="Markdown")
        else: # Asumsikan CallbackQuery
            await msg_or_query.message.reply_text(msg, parse_mode="Markdown")

    return ConversationHandler.END

# ====== Helper untuk mendaftarkan handler ke Application ======
def build_data_santri_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("data_santri", minta_akses),
            CallbackQueryHandler(admin_entry_data_santri, pattern=r"^admin:data_santri$"),
        ],
        states={
            PILIH_MODE: [
                CallbackQueryHandler(pilih_mode, pattern=r"^mode\|"),
                CallbackQueryHandler(navigasi_callback, pattern=r"^navi\|"),
                CallbackQueryHandler(navigasi_pencarian_callback, pattern=r"^navi_pencarian\|"),
                CallbackQueryHandler(tampilkan_detail_callback, pattern=r"^lihat\|"),
                CallbackQueryHandler(kembali_ke_menu_callback, pattern=r"^kembali_ke_menu$"),
            ],
            CARI_NIK: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_cari_nik)],
            CARI_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_cari_nama)],
        },
        fallbacks=[],
        name="data_santri_conv",
        persistent=False,
    )

