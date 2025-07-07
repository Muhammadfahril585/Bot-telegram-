import os
import uuid
from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, filters
)
from rembg.bg import remove

WAITING_PHOTO = range(1)

async def start_remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Kirimkan foto yang ingin dihapus background-nya.")
    return WAITING_PHOTO

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()

        # Simpan ke file sementara
        input_path = f"/tmp/{uuid.uuid4().hex}.png"
        output_path = f"/tmp/{uuid.uuid4().hex}_out.png"

        await file.download_to_drive(input_path)

        # Proses rembg dari file ke file
        with open(input_path, "rb") as i:
            with open(output_path, "wb") as o:
                o.write(remove(i.read()))

        # Kirim hasil ke user
        with open(output_path, "rb") as result:
            await update.message.reply_document(document=result, filename="hasil.png")

        # Bersihkan file
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        await update.message.reply_text(f"Gagal memproses gambar: {e}")

    return ConversationHandler.END

def get_remove_bg_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("hapus_bg", start_remove_bg)],
        states={
            WAITING_PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
        },
        fallbacks=[],
                                               )
