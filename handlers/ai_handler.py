from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.start import get_user_mode  # Untuk deteksi mode
from lib.knowledge_engine import jawab_berbasis_pengetahuan
from lib.ai_fallback import tanyakan_ke_model

async def handle_ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Hanya lanjut kalau user sedang di mode AI
    if get_user_mode(user_id) != "ai":
        return

    pertanyaan = update.message.text.strip()

    # Simpan pertanyaan untuk diproses setelah konfirmasi
    context.user_data["pertanyaan_pending"] = pertanyaan

    keyboard = [
        [
            InlineKeyboardButton("✅ Ya", callback_data="pertanyaan_pondok_ya"),
            InlineKeyboardButton("❌ Tidak", callback_data="pertanyaan_pondok_tidak"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤖 Apakah pertanyaan ini berkaitan dengan *PPTQ AL-ITQON GOWA*?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_pertanyaan_konfirmasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pilihan = query.data

    pertanyaan = context.user_data.get("pertanyaan_pending")
    if not pertanyaan:
        await query.edit_message_text("❌ Tidak ada pertanyaan yang diproses.")
        return

    if pilihan == "pertanyaan_pondok_ya":
        # Proses pakai pengetahuan pondok
        query.message.text = pertanyaan  # Override teks agar kompatibel
        update.message = query.message
        await jawab_berbasis_pengetahuan(update, context)
    else:
        # Fallback ke AI (OpenRouter)
        await query.edit_message_text("🤖 Sedang mencari jawaban terbaik...")
        jawaban = tanyakan_ke_model(pertanyaan)
        await query.message.reply_text(jawaban[:4096], parse_mode="Markdown")

    # Hapus pertanyaan pending
    context.user_data.pop("pertanyaan_pending", None)
