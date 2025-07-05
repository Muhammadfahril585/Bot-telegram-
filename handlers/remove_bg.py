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
    photo = update.message.photo[-1]  # Ambil kualitas tertinggi
    file = await photo.get_file()
    byte_stream = BytesIO()
    await file.download(out=byte_stream)

    byte_stream.seek(0)
    input_image = Image.open(byte_stream)

    output = remove(input_image)
    
    output_bytes = BytesIO()
    output.save(output_bytes, format="PNG")
    output_bytes.seek(0)

    await update.message.reply_document(document=output_bytes, filename="hasil.png")
    return ConversationHandler.END

def get_remove_bg_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("hapus_bg", start_remove_bg)],
        states={
            WAITING_PHOTO: [MessageHandler(filters.PHOTO, handle_photo)]
        },
        fallbacks=[],
  )
