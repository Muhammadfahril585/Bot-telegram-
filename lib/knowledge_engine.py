from lib.knowledge_base import cari_manual_berdasarkan_pertanyaan
from lib.ai_fallback import tanyakan_ke_model  # fungsi ke OpenRouter
from lib.ai_sql_engine import buat_sql_dari_pertanyaan, jalankan_query

# Tambahkan ini
async def proses_pertanyaan_pondok(update, context, pertanyaan):
    chat_id = update.effective_chat.id
    pertanyaan_lower = pertanyaan.lower()

    # Edukasi user (hanya sekali)
    if not context.user_data.get("sudah_diedukasi"):
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "📌 *Panduan Interaksi Bot:*\n"
                "Pertanyaan pondok akan dijawab berdasarkan data hafalan, halaqah, laporan, dll.\n"
                "Silakan bertanya 😊"
            ),
            parse_mode="Markdown"
        )
        context.user_data["sudah_diedukasi"] = True

    # 1. Manual Handler
    manual = cari_manual_berdasarkan_pertanyaan(pertanyaan_lower)
    if manual:
        await context.bot.send_message(chat_id=chat_id, text=manual[:4096], parse_mode="Markdown")
        return

    # 2. Rekap Bulanan
    info = ekstrak_info_rekap(pertanyaan_lower)
    if info["bulan"] and (info["halaqah"] or info["santri"]):
        conn = get_db()
        try:
            if info["santri"]:
                hasil = format_rekap_bulanan_santri(db=conn, bulan=info["bulan"], nama_santri=info["santri"], pekan=info["pekan"])
            else:
                hasil = format_rekap_bulanan(db=conn, bulan=info["bulan"], halaqah=info["halaqah"])
            await context.bot.send_message(chat_id=chat_id, text=hasil, parse_mode="Markdown")
            conn.close()
            return
        except Exception as e:
            print("❌ Rekap bulanan error:", e)
            await context.bot.send_message(chat_id=chat_id, text="⚠️ Terjadi kesalahan saat mengambil data rekap.")
            conn.close()
            return

    # 3. SQL AI
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    loading_msg = await context.bot.send_message(chat_id=chat_id, text="🤖 Saya sedang memahami permintaan Anda...")

    sql = buat_sql_dari_pertanyaan(pertanyaan_lower)
    if sql and sql.strip().lower().startswith("select"):
        hasil = jalankan_query(sql)
        await context.bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)
        await context.bot.send_message(chat_id=chat_id, text=hasil[:4096], parse_mode="Markdown")
        return

    # Fallback SQL gagal
    await context.bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)
    await context.bot.send_message(chat_id=chat_id, text="⚠️ Saya tidak berhasil membuat query dari permintaan tersebut.")

async def proses_pertanyaan_umum(update, context, pertanyaan):
    chat_id = update.effective_chat.id

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    jawaban = tanyakan_ke_model(pertanyaan)

    await context.bot.send_message(chat_id=chat_id, text=jawaban[:4096], parse_mode="Markdown")
