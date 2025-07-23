from lib.knowledge_base import cari_manual_berdasarkan_pertanyaan
from lib.ai_fallback import tanyakan_ke_model  # fungsi ke OpenRouter
from lib.ai_sql_engine import buat_sql_dari_pertanyaan, jalankan_query
from lib.rekap_parser import ekstrak_info_rekap
from lib.formatbulanan import format_rekap_bulanan, format_rekap_bulanan_santri
from database import get_db

# Tambahkan ini
async def proses_pertanyaan_pondok(update, context, pertanyaan):
    pertanyaan_lower = pertanyaan.lower()

    # Edukasi
    if not context.user_data.get("sudah_diedukasi"):
        await update.message.reply_text(
            "📌 *Panduan Interaksi Bot:*\n"
            "Pertanyaan pondok akan saya jawab berdasarkan data hafalan, halaqah, dll.\n"
            "Silakan bertanya 😊",
            parse_mode="Markdown"
        )
        context.user_data["sudah_diedukasi"] = True

    # Manual
    manual = cari_manual_berdasarkan_pertanyaan(pertanyaan_lower)
    if manual:
        await update.message.reply_text(manual[:4096], parse_mode="Markdown")
        return

    # Rekap Bulanan
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
            await update.message.reply_text("⚠️ Terjadi kesalahan saat mengambil data rekap.")
            conn.close()
            return

    # SQL AI
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    loading_msg = await update.message.reply_text("🤖 Saya sedang memahami permintaan Anda...")
    sql = buat_sql_dari_pertanyaan(pertanyaan_lower)
    if sql and sql.strip().lower().startswith("select"):
        hasil = jalankan_query(sql)
        await loading_msg.delete()
        await update.message.reply_text(hasil[:4096], parse_mode="Markdown")
        return

    await loading_msg.delete()
    await update.message.reply_text("⚠️ Saya tidak berhasil membuat query dari permintaan tersebut.")

async def proses_pertanyaan_umum(update, context, pertanyaan):
    chat_id = update.effective_chat.id

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    loading_msg = await context.bot.send_message(chat_id=chat_id, text="🤖 Saya sedang mencari jawaban terbaik...")

    jawaban = tanyakan_ke_model(pertanyaan)

    await context.bot.delete_message(chat_id=chat_id, message_id=loading_msg.message_id)
    await context.bot.send_message(chat_id=chat_id, text=jawaban[:4096], parse_mode="Markdown")
