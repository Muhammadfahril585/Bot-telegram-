from telegram import Update
from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler, filters, ContextTypes
)
from database import get_db

ADMIN_IDS = [970201320]  # Ganti dengan ID Telegram admin kamu

(
    PILIH_SANTRI,
    AYAH_NAMA,
    AYAH_TEMPAT_LAHIR,
    AYAH_TANGGAL_LAHIR,
    AYAH_NIK,
    AYAH_PENDIDIKAN,
    AYAH_PEKERJAAN,
    IBU_NAMA,
    IBU_TEMPAT_LAHIR,
    IBU_TANGGAL_LAHIR,
    IBU_NIK,
    IBU_PENDIDIKAN,
    IBU_PEKERJAAN,
) = range(13)

async def mulai_input_wali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Maaf, hanya admin yang bisa menggunakan perintah ini.")
        return ConversationHandler.END

    await update.message.reply_text("Masukkan nama lengkap santri:")
    return PILIH_SANTRI

async def pilih_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama = update.message.text.strip()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM santri_nama WHERE nama_lengkap = %s", (nama,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        await update.message.reply_text("Santri tidak ditemukan. Coba lagi:")
        return PILIH_SANTRI

    context.user_data['santri_nama_id'] = result[0]
    await update.message.reply_text("Masukkan nama Ayah Kandung:")
    return AYAH_NAMA

async def input_ayah_nama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ayah_nama'] = update.message.text.strip()
    await update.message.reply_text("Masukkan tempat lahir Ayah:")
    return AYAH_TEMPAT_LAHIR

async def input_ayah_tempat_lahir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ayah_tempat_lahir'] = update.message.text.strip()
    await update.message.reply_text("Masukkan tanggal lahir Ayah (YYYY-MM-DD):")
    return AYAH_TANGGAL_LAHIR

async def input_ayah_tanggal_lahir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ayah_tanggal_lahir'] = update.message.text.strip()
    await update.message.reply_text("Masukkan NIK Ayah:")
    return AYAH_NIK

async def input_ayah_nik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ayah_nik'] = update.message.text.strip()
    await update.message.reply_text("Masukkan pendidikan Ayah:")
    return AYAH_PENDIDIKAN

async def input_ayah_pendidikan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ayah_pendidikan'] = update.message.text.strip()
    await update.message.reply_text("Masukkan pekerjaan Ayah:")
    return AYAH_PEKERJAAN

async def input_ayah_pekerjaan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ayah_pekerjaan'] = update.message.text.strip()
    await update.message.reply_text("Masukkan nama Ibu Kandung:")
    return IBU_NAMA

async def input_ibu_nama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ibu_nama'] = update.message.text.strip()
    await update.message.reply_text("Masukkan tempat lahir Ibu:")
    return IBU_TEMPAT_LAHIR

async def input_ibu_tempat_lahir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ibu_tempat_lahir'] = update.message.text.strip()
    await update.message.reply_text("Masukkan tanggal lahir Ibu (YYYY-MM-DD):")
    return IBU_TANGGAL_LAHIR

async def input_ibu_tanggal_lahir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ibu_tanggal_lahir'] = update.message.text.strip()
    await update.message.reply_text("Masukkan NIK Ibu:")
    return IBU_NIK

async def input_ibu_nik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ibu_nik'] = update.message.text.strip()
    await update.message.reply_text("Masukkan pendidikan Ibu:")
    return IBU_PENDIDIKAN

async def input_ibu_pendidikan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ibu_pendidikan'] = update.message.text.strip()
    await update.message.reply_text("Masukkan pekerjaan Ibu:")
    return IBU_PEKERJAAN

async def input_ibu_pekerjaan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ibu_pekerjaan'] = update.message.text.strip()

    data = context.user_data
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO wali (
            santri_nama_id,
            ayah_nama, ayah_tempat_lahir, ayah_tanggal_lahir, ayah_nik, ayah_pendidikan, ayah_pekerjaan,
            ibu_nama, ibu_tempat_lahir, ibu_tanggal_lahir, ibu_nik, ibu_pendidikan, ibu_pekerjaan
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['santri_nama_id'],
        data['ayah_nama'], data['ayah_tempat_lahir'], data['ayah_tanggal_lahir'], data['ayah_nik'], data['ayah_pendidikan'], data['ayah_pekerjaan'],
        data['ibu_nama'], data['ibu_tempat_lahir'], data['ibu_tanggal_lahir'], data['ibu_nik'], data['ibu_pendidikan'], data['ibu_pekerjaan']
    ))
    conn.commit()
    conn.close()

    await update.message.reply_text("Data wali berhasil disimpan.")
    return ConversationHandler.END

async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Input dibatalkan.")
    return ConversationHandler.END

wali_conv = ConversationHandler(
    entry_points=[CommandHandler('input_wali', mulai_input_wali)],
    states={
        PILIH_SANTRI: [MessageHandler(filters.TEXT & ~filters.COMMAND, pilih_santri)],
        AYAH_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ayah_nama)],
        AYAH_TEMPAT_LAHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ayah_tempat_lahir)],
        AYAH_TANGGAL_LAHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ayah_tanggal_lahir)],
        AYAH_NIK: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ayah_nik)],
        AYAH_PENDIDIKAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ayah_pendidikan)],
        AYAH_PEKERJAAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ayah_pekerjaan)],
        IBU_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ibu_nama)],
        IBU_TEMPAT_LAHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ibu_tempat_lahir)],
        IBU_TANGGAL_LAHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ibu_tanggal_lahir)],
        IBU_NIK: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ibu_nik)],
        IBU_PENDIDIKAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ibu_pendidikan)],
        IBU_PEKERJAAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ibu_pekerjaan)],
    },
    fallbacks=[CommandHandler('batal', batal)],
  )
