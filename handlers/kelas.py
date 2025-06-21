from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from database import get_db

ADMIN_IDS = [970201320]  # Ganti dengan ID Telegram admin kamu

(MASUKKAN_NAMA, MASUKKAN_JENJANG, MASUKKAN_TINGKAT) = range(3)

async def mulai_input_kelas(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  if user_id not in ADMIN_IDS:
     await update.message.reply_text("Maaf, hanya admin yang bisa menggunakan perintah ini.")
     return ConversationHandler.END

  await update.message.reply_text("Masukkan *nama santri* yang ingin ditambahkan ke kelas:", parse_mode="Markdown")
  return MASUKKAN_NAMA

async def proses_nama_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama = update.message.text.strip()

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM santri_nama WHERE nama_lengkap = %s", (nama,))
    result = c.fetchone()
    conn.close()

    if result:
        context.user_data["id_santri"] = result[0]
        await update.message.reply_text("Masukkan jenjang kelas (contoh: SMP atau SMA):")
        return MASUKKAN_JENJANG
    else:
        await update.message.reply_text("Santri dengan nama tersebut tidak ditemukan. Pastikan penulisan sudah benar.")
        return ConversationHandler.END

async def proses_jenjang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jenjang = update.message.text.strip().upper()
    context.user_data["jenjang"] = jenjang
    await update.message.reply_text("Masukkan tingkat kelas (contoh: 1, 2, 3):")
    return MASUKKAN_TINGKAT

async def proses_tingkat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tingkat = update.message.text.strip()
    id_santri = context.user_data["id_santri"]
    jenjang = context.user_data["jenjang"]

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO kelas (santri_nama_id, jenjang, tingkat) VALUES (%s, %s, %s)", (id_santri, jenjang, tingkat))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"Data kelas berhasil disimpan: {jenjang} {tingkat}.")
    return ConversationHandler.END

async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Input dibatalkan.")
    return ConversationHandler.END

kelas_handler = ConversationHandler(
    entry_points=[CommandHandler("input_kelas", mulai_input_kelas)],
    states={
        MASUKKAN_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_nama_santri)],
        MASUKKAN_JENJANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_jenjang)],
        MASUKKAN_TINGKAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_tingkat)],
    },
    fallbacks=[CommandHandler("batal", batal)],
  )
