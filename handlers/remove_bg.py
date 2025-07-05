from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, filters
)
from rembg import remove
from io import BytesIO
from PIL import Image

# Status conversation
WAITING_PHOTO = range(1)

# Langkah awal: /hapus_bg
async def start_remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Silakan kirim foto yang ingin dihapus background-nya.")
    return WAITING_PHOTO

# Langkah setelah user kirim foto
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]  # Ambil resolusi tertinggi
        file = await photo.get_file()

        byte_stream = BytesIO()
        await file.download_to_drive(byte_stream)
        byte_stream.seek(0)

        # Pastikan gambar diubah ke format RGBA
        input_image = Image.open(byte_stream).convert("RGBA")

        # Hapus background
        output_image = remove(input_image)

        # Simpan ke buffer PNG
        output_bytes = BytesIO()
        output_image.save(output_bytes, format="PNG")
        output_bytes.seek(0)

        # Kirim hasil ke user
        await update.message.reply_document(document=output_bytes, filename="hasil.png")

    except Exception as e:
        await update.message.reply_text(f"Gagal memproses gambar: {e}")

    return ConversationHandler.END

# Fungsi handler utama
def get_remove_bg_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("hapus_bg", start_remove_bg)],
        states={
            WAITING_PHOTO: [MessageHandler(filters.PHOTO, handle_photo)]
        },
        fallbacks=[],
        )
