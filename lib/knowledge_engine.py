# lib/knowledge_engine.py
from telegram.constants import ChatAction
from lib.ai_fallback import tanyakan_ke_model  # SESUAIKAN dengan nama file antum

FOOTER = (
    "\n\n🤖 *Saya adalah asisten virtual PPTQ AL-ITQON GOWA.*\n"
    "Silakan ketik /start atau gunakan menu di kiri kolom ketik untuk fitur lengkap bot."
)


async def proses_pertanyaan_ai(update, context, pertanyaan: str):
    """
    Semua pertanyaan user akan dikirim ke model AI,
    lalu jawaban AI ditambah footer identitas asisten.
    Menampilkan indikator 'typing' + pesan 'sedang berfikir' terlebih dahulu.
    """
    chat_id = update.effective_chat.id

    # 1) Tampilkan indikator typing dan pesan "sedang berfikir"
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    thinking_msg = await update.message.reply_text(
        "⏳ *Tunggu sebentar, saya sedang berfikir...*",
        parse_mode="Markdown",
    )

    try:
        # 2) Panggil AI
        jawaban = tanyakan_ke_model(pertanyaan) or ""
        jawaban = jawaban.strip()

        jawaban_final = f"{jawaban}{FOOTER}"

        # 3) Hapus pesan “sedang berfikir”, lalu kirim jawaban final
        try:
            await thinking_msg.delete()
        except Exception:
            # kalau gagal hapus (misal sudah lama), abaikan saja
            pass

        await update.message.reply_text(
            jawaban_final,
            parse_mode="Markdown"
        )

    except Exception as e:
        print("❌ Error di proses_pertanyaan_ai:", e)
        # Coba edit pesan thinking jadi error message
        try:
            await thinking_msg.edit_text(
                "⚠️ Maaf, terjadi kesalahan saat memproses pertanyaan. Silakan coba lagi beberapa saat lagi.",
                parse_mode="Markdown"
            )
        except Exception:
            await update.message.reply_text(
                "⚠️ Maaf, terjadi kesalahan saat memproses pertanyaan. Silakan coba lagi beberapa saat lagi.",
                parse_mode="Markdown"
        )
