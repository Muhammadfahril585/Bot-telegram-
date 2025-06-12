import sqlite3
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

INPUT_NAMA = 1
DB_PATH = 'itqon.db'

# Daftar ID admin
ADMIN_IDS = [970201320]  # Ganti sesuai ID Telegram admin

def connect_db():
    return sqlite3.connect(DB_PATH)

async def mulai_tambah_santri(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Maaf, hanya admin yang bisa menggunakan perintah ini.")
        return ConversationHandler.END

    await update.message.reply_text("Masukkan nama lengkap santri yang akan ditambahkan:")
    return INPUT_NAMA

async def simpan_nama_santri(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    teks = update.message.text.strip()

    # Pisahkan nama berdasarkan baris atau koma
    nama_list = [nama.strip() for nama in teks.replace(',', '\n').split('\n') if nama.strip()]

    conn = connect_db()
    cursor = conn.cursor()
    berhasil = []
    gagal = []

    try:
        for nama in nama_list:
            try:
                cursor.execute("INSERT INTO santri_nama (nama_lengkap) VALUES (?)", (nama,))
                berhasil.append(nama)
            except sqlite3.IntegrityError:
                gagal.append(nama)

        conn.commit()

        pesan = ""
        if berhasil:
            pesan += "*Berhasil ditambahkan:*\n" + '\n'.join(f"- {n}" for n in berhasil) + "\n\n"
        if gagal:
            pesan += "*Gagal (sudah ada di database):*\n" + '\n'.join(f"- {n}" for n in gagal)

        await update.message.reply_text(pesan, parse_mode='Markdown')

    finally:
        conn.close()

    return ConversationHandler.END

async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Proses dibatalkan.")
    return ConversationHandler.END

tambah_santri_handler = ConversationHandler(
    entry_points=[CommandHandler('tambah_santri', mulai_tambah_santri)],
    states={
        INPUT_NAMA: [MessageHandler(filters.TEXT & (~filters.COMMAND), simpan_nama_santri)],
    },
    fallbacks=[CommandHandler('batal', batal)],
)
