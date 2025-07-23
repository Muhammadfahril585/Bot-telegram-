from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from lib.knowledge_base import cari_manual_berdasarkan_pertanyaan
from lib.ai_fallback import tanyakan_ke_model
from lib.ai_sql_engine import buat_sql_dari_pertanyaan, jalankan_query

# Tahap awal: edukasi dan pertanyaan konfirmasi
async def tanggapi_pertanyaan_awal(update, context):
    pertanyaan = update.message.text.strip()
    context.user_data["pertanyaan_terakhir"] = pertanyaan

    if not context.user_data.get("sudah_diedukasi"):
        await update.message.reply_text(
            "📌 *Panduan Interaksi Bot:*\n"
            "Silakan ajukan pertanyaan.\n"
            "Contoh:\n- _Siapa santri dengan hafalan terbanyak?_\n- _Tolong tampilkan rekap bulan Juli._",
            parse_mode="Markdown"
        )
        context.user_data["sudah_diedukasi"] = True

    keyboard = [
        [
            InlineKeyboardButton("✅ Ya", callback_data="pertanyaan_pondok_ya"),
            InlineKeyboardButton("❌ Tidak", callback_data="pertanyaan_pondok_tidak"),
        ]
    ]
    await update.message.reply_text(
        "🤔 *Apakah pertanyaan ini berkaitan dengan PPTQ AL-ITQON GOWA?*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# Callback tombol konfirmasi
async def handle_pertanyaan_konfirmasi(update, context):
    query = update.callback_query
    await query.answer()
    pilihan = query.data
    pertanyaan = context.user_data.get("pertanyaan_terakhir", "").lower()

    if not pertanyaan:
        await query.edit_message_text("❌ Tidak ada pertanyaan untuk diproses.")
        return

    if pilihan == "pertanyaan_pondok_ya":
        await jawab_pertanyaan_pondok(query, context, pertanyaan)
    else:
        # 🧠 Kirim ke AI Umum
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
        loading_msg = await query.message.reply_text("🤖 Saya sedang mencari jawaban terbaik...")
        
        jawaban = tanyakan_ke_model(pertanyaan)
        
        await loading_msg.delete()
        await query.message.reply_text(jawaban[:4096], parse_mode="Markdown")

    # Bersihkan cache pertanyaan
    context.user_data.pop("pertanyaan_terakhir", None)
# Penjawab jika konfirmasi "Ya"
async def jawab_pertanyaan_pondok(query, context, pertanyaan):
    # 1. Manual
    manual = cari_manual_berdasarkan_pertanyaan(pertanyaan)
    if manual:
        await query.edit_message_text(manual[:4096], parse_mode="Markdown")
        return

    # 2. Rekap
    info = ekstrak_info_rekap(pertanyaan)
    if info["bulan"] and (info["halaqah"] or info["santri"]):
        try:
            if info["santri"]:
                hasil = format_rekap_bulanan_santri(bulan=info["bulan"], nama_santri=info["santri"], pekan=info["pekan"])
            else:
                hasil = format_rekap_bulanan(bulan=info["bulan"], halaqah=info["halaqah"])
            await query.edit_message_text(hasil[:4096], parse_mode="Markdown")
            return
        except Exception as e:
            print("❌ Rekap bulanan error:", e)
            await query.edit_message_text("⚠️ Terjadi kesalahan saat mengambil data rekap.")
            return

    # 3. SQL dari AI
    await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
    sql = buat_sql_dari_pertanyaan(pertanyaan)
    if sql and sql.strip().lower().startswith("select"):
        hasil = jalankan_query(sql)
        await query.edit_message_text(hasil[:4096], parse_mode="Markdown")
        return

    await query.edit_message_text("⚠️ Saya tidak berhasil membuat query dari permintaan tersebut.")
