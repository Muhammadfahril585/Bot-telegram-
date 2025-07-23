from lib.knowledge_base import cari_manual_berdasarkan_pertanyaan
from lib.ai_fallback import tanyakan_ke_model  # fungsi ke OpenRouter
from lib.ai_sql_engine import buat_sql_dari_pertanyaan, jalankan_query

async def jawab_berbasis_pengetahuan(update, context):
    pertanyaan = update.message.text.strip()
    pertanyaan_lower = pertanyaan.lower()

    # Awali dengan edukasi ke user setiap kali kirim pesan
    if not context.user_data.get("sudah_diedukasi"):
        await update.message.reply_text(
            "📌 *Panduan Interaksi Bot:*\n"
            "1. Untuk akses data pondok Al-ITQON (hafalan, halaqah, laporan, dst), awali dengan kata *tolong*.\n"
            "   Contoh: _Tolong tampilkan santri dengan hafalan terbanyak._\n"
            "2. Jika pertanyaan umum (motivasi, terjemahan, nasihat), cukup kirim tanpa kata 'tolong'.\n\n"
            "Silakan bertanya 😊",
            parse_mode="Markdown"
        )
        context.user_data["sudah_diedukasi"] = True

    # Hanya proses ke data pondok jika ada kata "tolong"
    if "tolong" in pertanyaan_lower:
        # 1. Handler manual
        manual = cari_manual_berdasarkan_pertanyaan(pertanyaan_lower)
        if manual:
            await update.message.reply_text(manual[:4096],
            parse_mode="Markdown")
            return
        # Deteksi jika pertanyaan berkaitan dengan rekap bulanan
        info = ekstrak_info_rekap(pertanyaan_lower)
        if info["bulan"] and (info["halaqah"] or info["santri"]):
            conn = get_db()
            try:
                if info["santri"]:
                    hasil = format_rekap_bulanan_santri(db=conn, bulan=info["bulan"], nama_santri=info["santri"], pekan=info["pekan"])
                else:
                    hasil = format_rekap_bulanan(db=conn, bulan=info["bulan"], halaqah=info["halaqah"])
                await update.message.reply_text(hasil, parse_mode="Markdown")
                conn.close()
                return
            except Exception as e:
                print("❌ Rekap bulanan error:", e)
                await update.message.reply_text("⚠️ Terjadi kesalahan saat mengambil data rekap.")
                conn.close()
                return                                                                                                                                                           
        # 3. SQL AI Generator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        loading_msg = await update.message.reply_text("🤖 Saya sedang memahami permintaan Anda...")
        sql = buat_sql_dari_pertanyaan(pertanyaan_lower)
        if sql and sql.strip().lower().startswith("select"):
            hasil = jalankan_query(sql)
            await loading_msg.delete()
            await update.message.reply_text(hasil[:4096],
            parse_mode="Markdown")
            return

        # Jika SQL gagal
        await loading_msg.delete()
        await update.message.reply_text("⚠️ Saya tidak berhasil membuat query dari permintaan tersebut.")
        return

    # Fallback untuk pertanyaan umum di luar pondok
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    loading_msg = await update.message.reply_text("🤖 Saya sedang mencari jawaban terbaik...")
    jawaban = tanyakan_ke_model(pertanyaan)
    await loading_msg.delete()
    await update.message.reply_text(jawaban[:4096],
    parse_mode="Markdown")



