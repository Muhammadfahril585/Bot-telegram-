# lib/knowledge_engine.py

from lib.ai_fallback import tanyakan_ke_model  # SESUAIKAN dengan nama file antum

FOOTER = (
    "\n\n🤖 *Saya adalah asisten virtual PPTQ AL-ITQON GOWA.*\n"
    "Silakan ketik /start atau gunakan menu di kiri kolom ketik untuk fitur lengkap bot."
)


async def proses_pertanyaan_ai(update, context, pertanyaan: str):
    """
    Semua pertanyaan user akan dikirim ke model AI,
    lalu jawaban AI ditambah footer identitas asisten.
    """
    try:
        jawaban = tanyakan_ke_model(pertanyaan) or ""
        jawaban = jawaban.strip()

        # Tambahkan footer
        jawaban_final = f"{jawaban}{FOOTER}"

        await update.message.reply_text(
            jawaban_final,
            parse_mode="Markdown"
        )

    except Exception as e:
        print("❌ Error di proses_pertanyaan_ai:", e)
        await update.message.reply_text(
            "⚠️ Maaf, terjadi kesalahan saat memproses pertanyaan. Silakan coba lagi beberapa saat lagi.",
            parse_mode="Markdown"
        )
