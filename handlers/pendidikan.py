import sqlite3
from telegram import Update
from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler, ContextTypes, filters
)
DB_PATH = 'itqon.db'

ADMIN_IDS = [970201320]  # Ganti dengan ID Telegram admin kamu

# STATE
(
    PILIH_SANTRI, NAMA_LEMBAGA, NPNS, JENIS_PENDIDIKAN, LOKASI_LEMBAGA,
    PROVINSI, TAHUN_LULUS, ALAMAT, KABUPATEN, KECAMATAN
) = range(10)

def connect_db():
    return sqlite3.connect(DB_PATH)

async def mulai_input_pendidikan(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  if user_id not in ADMIN_IDS:
     await update.message.reply_text("Maaf, hanya admin yang bisa menggunakan perintah ini.")
     return ConversationHandler.END

  await update.message.reply_text("Masukkan nama lengkap santri:")
  return PILIH_SANTRI

async def pilih_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama = update.message.text.strip()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM santri_nama WHERE nama_lengkap = ?", (nama,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        await update.message.reply_text("Santri tidak ditemukan. Coba lagi:")
        return PILIH_SANTRI

    context.user_data['santri_nama_id'] = result[0]
    await update.message.reply_text("Masukkan nama lembaga pendidikan:")
    return NAMA_LEMBAGA

async def input_nama_lembaga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nama_lembaga'] = update.message.text.strip()
    await update.message.reply_text("Masukkan NPNS:")
    return NPNS

async def input_npns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['npns'] = update.message.text.strip()
    await update.message.reply_text("Masukkan jenis pendidikan:")
    return JENIS_PENDIDIKAN

async def input_jenis_pendidikan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['jenis_pendidikan'] = update.message.text.strip()
    await update.message.reply_text("Masukkan lokasi lembaga:")
    return LOKASI_LEMBAGA

async def input_lokasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lokasi_lembaga'] = update.message.text.strip()
    await update.message.reply_text("Masukkan provinsi:")
    return PROVINSI

async def input_provinsi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['provinsi'] = update.message.text.strip()
    await update.message.reply_text("Masukkan tahun lulus:")
    return TAHUN_LULUS

async def input_tahun_lulus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['tahun_lulus'] = update.message.text.strip()
    await update.message.reply_text("Masukkan alamat:")
    return ALAMAT

async def input_alamat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['alamat'] = update.message.text.strip()
    await update.message.reply_text("Masukkan kabupaten:")
    return KABUPATEN

async def input_kabupaten(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['kabupaten'] = update.message.text.strip()
    await update.message.reply_text("Masukkan kecamatan:")
    return KECAMATAN

async def input_kecamatan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['kecamatan'] = update.message.text.strip()
    data = context.user_data

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pendidikan (
            santri_nama_id, nama_lembaga, npns, jenis_pendidikan, lokasi_lembaga,
            provinsi, tahun_lulus, alamat, kabupaten, kecamatan
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['santri_nama_id'], data['nama_lembaga'], data['npns'], data['jenis_pendidikan'],
        data['lokasi_lembaga'], data['provinsi'], data['tahun_lulus'],
        data['alamat'], data['kabupaten'], data['kecamatan']
    ))
    conn.commit()
    conn.close()

    await update.message.reply_text("Data pendidikan berhasil disimpan.")
    return ConversationHandler.END

async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Input dibatalkan.")
    return ConversationHandler.END

pendidikan_conv = ConversationHandler(
    entry_points=[CommandHandler('input_pendidikan', mulai_input_pendidikan)],
    states={
        PILIH_SANTRI: [MessageHandler(filters.TEXT & ~filters.COMMAND, pilih_santri)],
        NAMA_LEMBAGA: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_nama_lembaga)],
        NPNS: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_npns)],
        JENIS_PENDIDIKAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_jenis_pendidikan)],
        LOKASI_LEMBAGA: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_lokasi)],
        PROVINSI: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_provinsi)],
        TAHUN_LULUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_tahun_lulus)],
        ALAMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_alamat)],
        KABUPATEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_kabupaten)],
        KECAMATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_kecamatan)],
    },
    fallbacks=[CommandHandler('batal', batal)],
)
