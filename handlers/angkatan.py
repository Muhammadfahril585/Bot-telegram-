from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
import sqlite3

DB_PATH = 'itqon.db'

ADMIN_IDS = [970201320]  # Ganti dengan ID Telegram admin kamu

(MASUKKAN_NAMA, MASUKKAN_ANGKATAN) = range(2)

async def mulai_input_angkatan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Maaf, hanya admin yang bisa menggunakan perintah ini.")
        return ConversationHandler.END
    await update.message.reply_text("Masukkan *nama santri* yang ingin ditambahkan angkatannya:", parse_mode="Markdown")
    return MASUKKAN_NAMA

async def proses_nama_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama = update.message.text.strip()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM santri_nama WHERE nama_lengkap = ?", (nama,))
    result = c.fetchone()
    conn.close()
    if result:
        context.user_data["id_santri"] = result[0]
        await update.message.reply_text("Masukkan angkatan (contoh: 2023):")
        return MASUKKAN_ANGKATAN
    else:
        await update.message.reply_text("Santri dengan nama tersebut tidak ditemukan. Pastikan penulisan sudah benar.")
        return ConversationHandler.END

async def proses_angkatan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    angkatan = update.message.text.strip()
    id_santri = context.user_data["id_santri"]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Cek apakah santri sudah punya angkatan
    c.execute("SELECT id FROM angkatan WHERE santri_nama_id = ?", (id_santri,))
    if c.fetchone():
        await update.message.reply_text("❗ Santri ini sudah memiliki data angkatan. Gunakan fitur edit jika ingin mengubah.")
    conn.close()
    return ConversationHandler.END

# Jika belum ada, simpan
    c.execute("INSERT INTO angkatan (santri_nama_id, angkatan) VALUES (?, ?)", (id_santri, angkatan))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Data angkatan berhasil disimpan: {angkatan}.")
    return ConversationHandler.END

# Fungsi batal input
async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Input dibatalkan.")
    return ConversationHandler.END

# Handler untuk input angkatan
angkatan_handler = ConversationHandler(
    entry_points=[CommandHandler("input_angkatan", mulai_input_angkatan)],
    states={
        MASUKKAN_NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_nama_santri)],
        MASUKKAN_ANGKATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_angkatan)],
    },
    fallbacks=[CommandHandler("batal", batal)],
)
