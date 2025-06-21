from database import get_db
from telegram import Update
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, ContextTypes

(
    NAMA,
    NIS,
    NIK,
    NOMOR_KK,
    TEMPAT_LAHIR,
    TANGGAL_LAHIR,
    JENIS_KELAMIN,
    AGAMA,
    ANAK_KE,
    PROVINSI,
    KABUPATEN,
    KECAMATAN,
    ALAMAT,
) = range(13)

ADMIN_IDS = [970201320]  # Ganti dengan ID Telegram admin kamu

async def mulai_input_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  user_id = update.effective_user.id
  if user_id not in ADMIN_IDS:
     await update.message.reply_text("Maaf, hanya admin yang bisa menggunakan perintah ini.")
     return ConversationHandler.END

  await update.message.reply_text("Masukkan nama lengkap santri untuk diinput detailnya:")
  return NAMA

async def input_nama(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nama = update.message.text.strip()

    # Ambil ID dari nama_santri
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM santri_nama WHERE nama_lengkap = %s", (nama,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        await update.message.reply_text("Nama tidak ditemukan di database. Masukkan nama yang sudah terdaftar.")
        return NAMA

    context.user_data['santri_nama_id'] = result[0]
    context.user_data['nama_lengkap'] = nama

    await update.message.reply_text("Masukkan NIS:")
    return NIS

async def input_nis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['nis'] = update.message.text.strip()
    await update.message.reply_text("Masukkan NIK:")
    return NIK

async def input_nik(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['nik'] = update.message.text.strip()
    await update.message.reply_text("Masukkan Nomor KK:")
    return NOMOR_KK

async def input_nomor_kk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['nomor_kk'] = update.message.text.strip()
    await update.message.reply_text("Masukkan Tempat Lahir:")
    return TEMPAT_LAHIR

async def input_tempat_lahir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['tempat_lahir'] = update.message.text.strip()
    await update.message.reply_text("Masukkan Tanggal Lahir (YYYY-MM-DD):")
    return TANGGAL_LAHIR

async def input_tanggal_lahir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['tanggal_lahir'] = update.message.text.strip()
    await update.message.reply_text("Masukkan Jenis Kelamin (L/P):")
    return JENIS_KELAMIN

async def input_jenis_kelamin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    jk = update.message.text.strip().upper()
    if jk not in ['L', 'P']:
        await update.message.reply_text("Jenis Kelamin harus 'L' atau 'P'. Masukkan ulang:")
        return JENIS_KELAMIN
    context.user_data['jenis_kelamin'] = jk
    await update.message.reply_text("Masukkan Agama:")
    return AGAMA

async def input_agama(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['agama'] = update.message.text.strip()
    await update.message.reply_text("Masukkan Anak Ke:")
    return ANAK_KE

async def input_anak_ke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['anak_ke'] = update.message.text.strip()
    await update.message.reply_text("Masukkan Provinsi:")
    return PROVINSI

async def input_provinsi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['provinsi'] = update.message.text.strip()
    await update.message.reply_text("Masukkan Kabupaten:")
    return KABUPATEN

async def input_kabupaten(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['kabupaten'] = update.message.text.strip()
    await update.message.reply_text("Masukkan Kecamatan:")
    return KECAMATAN

async def input_kecamatan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['kecamatan'] = update.message.text.strip()
    await update.message.reply_text("Masukkan Alamat Lengkap:")
    return ALAMAT

async def input_alamat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['alamat'] = update.message.text.strip()

    data = context.user_data
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO santri (
            santri_nama_id, nis, nik, nomor_kk, tempat_lahir, tanggal_lahir, jenis_kelamin, agama, anak_ke,
            provinsi, kabupaten, kecamatan, alamat
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['santri_nama_id'], data['nis'], data['nik'], data['nomor_kk'],
        data['tempat_lahir'], data['tanggal_lahir'], data['jenis_kelamin'],
        data['agama'], data['anak_ke'],
        data['provinsi'], data['kabupaten'], data['kecamatan'], data['alamat']
    ))
    conn.commit()
    conn.close()

    await update.message.reply_text("✅ Data detail santri lengkap berhasil disimpan.")
    return ConversationHandler.END

async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Proses input data dibatalkan.")
    return ConversationHandler.END

detail_santri_handler = ConversationHandler(
    entry_points=[CommandHandler('input_detail_santri', mulai_input_detail)],
    states={
      NAMA: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_nama)],
      NIS: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_nis)],
      NIK: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_nik)],
      TEMPAT_LAHIR: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_tempat_lahir)],
      TANGGAL_LAHIR: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_tanggal_lahir)],
      JENIS_KELAMIN: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_jenis_kelamin)],
      AGAMA: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_agama)],
      ANAK_KE: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_anak_ke)],
      NOMOR_KK: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_nomor_kk)],
      PROVINSI: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_provinsi)],
      KABUPATEN: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_kabupaten)],
      KECAMATAN: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_kecamatan)],
      ALAMAT: [MessageHandler(filters.TEXT & (~filters.COMMAND), input_alamat)],
    },
    fallbacks=[CommandHandler('batal', batal)],
)
