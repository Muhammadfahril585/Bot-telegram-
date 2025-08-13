from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from utils.gsheet import get_sheet
import datetime
import asyncio
import telegram  # untuk telegram.error.BadRequest

# ================== KONFIGURASI ==================
NAMA_SHEET = "DATA_SANTRI"
JUMLAH_PER_HALAMAN = 10
PASSWORD_BOT = "AL2020"

# State conversation
INPUT_PASSWORD, PILIH_MODE, CARI_NIK = range(3)
# =================================================

def get_data_santri():
    sheet = get_sheet(NAMA_SHEET)
    # Ambil dari baris ke-3 ke bawah (sesuai kode awal)
    return sheet.get_all_values()[2:]

# ====== STEP 1: minta password dulu ======
async def data_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔑 Masukkan *kata sandi* untuk mengakses data santri:", parse_mode="Markdown")
    return INPUT_PASSWORD

async def cek_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pwd = (update.message.text or "").strip()
    if pwd != PASSWORD_BOT:
        await update.message.reply_text("❌ Kata sandi *salah*. Akses ditolak.", parse_mode="Markdown")
        return ConversationHandler.END

    # Tanda user sudah terverifikasi untuk fitur ini
    context.user_data["verified_data_santri"] = True

    keyboard = [
        [InlineKeyboardButton("🔍 Cari Berdasarkan NIK", callback_data="mode|nik")],
        [InlineKeyboardButton("📑 Lihat Daftar Nama Santri", callback_data="mode|nama")]
    ]
    await update.message.reply_text(
        "✅ Berhasil! \n\n📋 *Pilih Mode Pencarian Data Santri:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return PILIH_MODE
# =========================================

async def pilih_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Pastikan sudah verifikasi (jaga-jaga bila user lompat)
    if not context.user_data.get("verified_data_santri"):
        await query.edit_message_text("🔒 Akses dikunci. Silakan mulai ulang perintah dan masukkan kata sandi.")
        return ConversationHandler.END

    mode = query.data.split("|")[1]
    context.user_data["santri_data"] = get_data_santri()

    if mode == "nik":
        await query.edit_message_text(
            text="✍️ Silakan *masukkan NIK* santri yang ingin dicari:",
            parse_mode='Markdown'
        )
        return CARI_NIK
    elif mode == "nama":
        context.user_data["halaman"] = 0
        await tampilkan_nama_inline(query, context)
        return PILIH_MODE

async def proses_cari_nik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_data_santri"):
        await update.message.reply_text("🔒 Akses dikunci. Silakan mulai ulang perintah dan masukkan kata sandi.")
        return ConversationHandler.END

    nik_input = update.message.text.strip()
    data = context.user_data.get("santri_data", get_data_santri())

    for row in data:
        if len(row) > 1 and row[1] == nik_input:
            return await tampilkan_detail(row, update)

    await update.message.reply_text("❌ Data tidak ditemukan untuk NIK tersebut.")
    return ConversationHandler.END

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

    await query.edit_message_text(
        text="📋 *Pilih Nama Santri:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def navigasi_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not context.user_data.get("verified_data_santri"):
        await query.edit_message_text("🔒 Akses dikunci. Silakan mulai ulang perintah dan masukkan kata sandi.")
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
        await query.edit_message_text("🔒 Akses dikunci. Silakan mulai ulang perintah dan masukkan kata sandi.")
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
            await msg_or_query.message.reply_photo(
                photo=file_id,
                caption=msg,
                parse_mode="Markdown"
            )
        except Exception as e:
            await msg_or_query.message.reply_text(
                f"⚠️ Gagal menampilkan foto:\n{e}\n\n{msg}",
                parse_mode="Markdown"
            )
    else:
        await msg_or_query.message.reply_text(msg, parse_mode="Markdown")

    return ConversationHandler.END

# ====== Helper untuk mendaftarkan handler ke Application ======
def build_data_santri_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("data_santri", data_santri)],
        states={
            INPUT_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, cek_password)],
            PILIH_MODE: [
                CallbackQueryHandler(pilih_mode, pattern=r"^mode\|"),
                CallbackQueryHandler(navigasi_callback, pattern=r"^navi\|"),
                CallbackQueryHandler(tampilkan_detail_callback, pattern=r"^lihat\|"),
            ],
            CARI_NIK: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_cari_nik)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        name="data_santri_conv",
        persistent=False,
    )
