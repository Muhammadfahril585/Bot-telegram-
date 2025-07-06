from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, filters
)
from rembg import remove
from io import BytesIO

WAITING_PHOTO = range(1)

async def start_remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Kirimkan foto untuk dihapus background-nya.")
    return WAITING_PHOTO

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]  # Ambil resolusi tertinggi
        file = await photo.get_file()

        # ✅ Download foto ke BytesIO
        buffer = BytesIO()
        await file.download_to_drive(buffer)
        buffer.seek(0)

        # ✅ Ubah ke bytes
        image_bytes = buffer.read()

        # ✅ Hapus background
        result = remove(image_bytes)

        # ✅ Kirim hasil
        result_io = BytesIO(result)
        result_io.name = "hasil.png"
        result_io.seek(0)

        await update.message.reply_document(document=result_io)

    except Exception as e:
        await update.message.reply_text(f"Gagal memproses gambar: {str(e)}")

    return ConversationHandler.END

def get_remove_bg_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("hapus_bg", start_remove_bg)],
        states={
            WAITING_PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
        },
        fallbacks=[],
    )
