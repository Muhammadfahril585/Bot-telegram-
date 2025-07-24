# handlers/ai_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from lib.knowledge_engine import proses_pertanyaan_pondok, proses_pertanyaan_umum
from handlers.start import get_user_mode  # Cek mode user

async def handle_ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Cek apakah user dalam mode AI
    if get_user_mode(user_id) != "ai":
        return

    # Simpan dulu pertanyaan user
    pertanyaan = update.message.text.strip()
    context.user_data["last_question"] = pertanyaan

    # Kirim pertanyaan "berkaitan pondok?" + tombol
    keyboard = [
        [
            InlineKeyboardButton("✅ Ya", callback_data="pertanyaan_pondok"),
            InlineKeyboardButton("❌ Tidak", callback_data="pertanyaan_umum")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🤔 Afwan, apakah pertanyaan ini berkaitan dengan *pondok*?\n"
        "_(misalnya tentang santri, halaqah, hafalan, laporan, dll. jika tidak berhubungan pilih TIDAK)_",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Callback handler untuk respon tombol
async def handle_pertanyaan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pertanyaan = context.user_data.get("last_question", "")
    if not pertanyaan:
        await query.edit_message_text("⚠️ Pertanyaan tidak ditemukan.")
        return

    msg_id = query.message.message_id
    chat_id = query.message.chat_id

    if query.data == "pertanyaan_pondok":
        await query.edit_message_text("🤖 Saya sedang memahami permintaan Anda...")
        await proses_pertanyaan_pondok(update, context, pertanyaan)
    else:
        await query.edit_message_text("🤖 Saya sedang mencari jawaban terbaik...")
        await proses_pertanyaan_umum(update, context, pertanyaan)

    # Hapus pesan loading setelah jawaban selesai dikirim
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except Exception as e:
        print("Gagal menghapus pesan loading:", e)
