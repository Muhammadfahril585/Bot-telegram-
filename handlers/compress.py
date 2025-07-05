from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters
)
import os
import subprocess

TEMP_DIR = "videos"
os.makedirs(TEMP_DIR, exist_ok=True)

SELECT_MODE, WAITING_VIDEO = range(2)

async def start_compress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📎 Kecil (~280x158)", callback_data="280x158")],
        [InlineKeyboardButton("📎 Medium (~424x239)", callback_data="424x239")],
        [InlineKeyboardButton("📎 Besar (~848x478)", callback_data="848x478")]
    ]
    await update.message.reply_text(
        "Pilih ukuran kompresi yang kamu inginkan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECT_MODE

async def select_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    resolution = query.data
    context.user_data["target_res"] = resolution

    await query.edit_message_text(
        f"Resolusi {resolution} dipilih.\nSilakan kirim video yang ingin dikompres."
    )
    return WAITING_VIDEO

async def compress_video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    if not video:
        await update.message.reply_text("Harap kirim video, bukan file lain.")
        return WAITING_VIDEO

    resolution = context.user_data.get("target_res", "424x239")  # default Medium
    width, height = resolution.split("x")

    await update.message.reply_text(
        f"📥 Menerima video dan mengompres ke {width}x{height}..."
    )

    file = await video.get_file()
    original_path = os.path.join(TEMP_DIR, f"{update.message.message_id}_ori.mp4")
    compressed_path = os.path.join(TEMP_DIR, f"{update.message.message_id}_compressed.mp4")

    await file.download_to_drive(original_path)

    cmd = [
        "ffmpeg", "-i", original_path,
        "-vcodec", "libx264",
        "-b:v", "500k",
        "-vf", f"scale={width}:{height}",
        "-preset", "fast",
        compressed_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    await update.message.reply_video(video=open(compressed_path, "rb"))
    os.remove(original_path)
    os.remove(compressed_path)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kompresi dibatalkan.")
    return ConversationHandler.END

def get_compress_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("compress", start_compress)],
        states={
            SELECT_MODE: [CallbackQueryHandler(select_mode)],
            WAITING_VIDEO: [MessageHandler(filters.VIDEO, compress_video_handler)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
