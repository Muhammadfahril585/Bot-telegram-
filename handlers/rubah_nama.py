from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, filters
)
from db import get_db

# State untuk Conversation
INPUT_PERUBAHAN_NAMA = 1

async def rubah_nama_awal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 Silakan masukkan daftar perubahan nama santri, contoh:\n\n"
        "`Ahmad al faruq = Ahmad Faruq`\n`Muh Fahril = Laode Muh Fahril`\n\n"
        "Satu baris satu nama ya.",
        parse_mode="Markdown"
    )
    return INPUT_PERUBAHAN_NAMA

async def proses_perubahan_nama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    db = get_db()
    cursor = db.cursor()
    hasil = []

    for baris in text.strip().split("\n"):
        if "=" not in baris:
            hasil.append(f"❌ Format salah: `{baris}`")
            continue

        nama_lama, nama_baru = map(str.strip, baris.split("=", 1))

        if not nama_baru:
            hasil.append(f"⚠️ Nama baru kosong: `{baris}`")
            continue

        cursor.execute("SELECT 1 FROM santri WHERE nama = %s", (nama_lama,))
        if cursor.fetchone():
            cursor.execute("UPDATE santri SET nama = %s WHERE nama = %s", (nama_baru, nama_lama))
            hasil.append(f"✅ {nama_lama} → *{nama_baru}*")
        else:
            hasil.append(f"⚠️ Tidak ditemukan: `{nama_lama}`")

    db.commit()
    db.close()

    await update.message.reply_text(
        "*Hasil Perubahan Nama:*\n" + "\n".join(hasil),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Perubahan dibatalkan.")
    return ConversationHandler.END

# Export handler-nya langsung
rubah_nama_handler = ConversationHandler(
    entry_points=[CommandHandler("rubah_nama", rubah_nama_awal)],
    states={
        INPUT_PERUBAHAN_NAMA: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, proses_perubahan_nama)
        ],
    },
    fallbacks=[CommandHandler("batal", batal)],
)
