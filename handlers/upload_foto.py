from database import get_db
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

UPLOAD = {}

async def mulai_upload_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kirim foto santri ini lalu ketik ID santri:")
    return 1

async def terima_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ Itu bukan foto. Kirim ulang.")
        return 1

    file_id = update.message.photo[-1].file_id  # ambil kualitas tertinggi
    context.user_data['file_id'] = file_id
    await update.message.reply_text("Sekarang kirim ID santri yang ingin dikaitkan:")
    return 2

async def simpan_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        santri_id = int(update.message.text.strip())
        file_id = context.user_data.get('file_id')

        if not file_id:
            await update.message.reply_text("❌ Belum ada foto.")
            return ConversationHandler.END

        # Simpan ke database
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE santri_nama SET foto_id = %s WHERE id = %s", (file_id, santri_id))
        conn.commit()
        conn.close()

        await update.message.reply_text("✅ Foto berhasil disimpan.")
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal menyimpan foto: {e}")
    return ConversationHandler.END

upload_foto_handler = ConversationHandler(
    entry_points=[CommandHandler("upload_foto", mulai_upload_foto)],
    states={
        1: [MessageHandler(filters.PHOTO, terima_foto)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_foto)],
    },
    fallbacks=[],
)
