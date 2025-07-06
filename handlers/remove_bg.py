from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, filters
)
from rembg import remove
from io import BytesIO
from PIL import Image

WAITING_PHOTO = range(1)

async def start_remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Silakan kirim foto yang ingin dihapus background-nya.")
    return WAITING_PHOTO

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()

        input_io = BytesIO()
        await file.download_to_drive(input_io)
        input_io.seek(0)

        # ✅ Baca sebagai bytes
        input_bytes = input_io.read()

        # ✅ Proses dengan rembg
        output_bytes = remove(input_bytes)

        # ✅ Simpan ke file sementara untuk dikirim
        result_io = BytesIO(output_bytes)
        result_io.seek(0)

        await update.message.reply_document(document=result_io, filename="hasil.png")

    except Exception as e:
        await update.message.reply_text(f"Gagal memproses gambar: {e}")

    return ConversationHandler.END

def get_remove_bg_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("hapus_bg", start_remove_bg)],
        states={
            WAITING_PHOTO: [MessageHandler(filters.PHOTO, handle_photo)]
        },
        fallbacks=[],
    )
