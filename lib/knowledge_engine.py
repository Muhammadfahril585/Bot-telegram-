from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

from lib.knowledge_base import cari_manual_berdasarkan_pertanyaan
from lib.ai_fallback import tanyakan_ke_model
from lib.ai_sql_engine import buat_sql_dari_pertanyaan, jalankan_query
from lib.rekap import ekstrak_info_rekap, format_rekap_bulanan, format_rekap_bulanan_santri

# Fungsi utama
async def jawab_berbasis_pengetahuan(update, context):
    pertanyaan = update.message.text.strip()
    context.user_data["pertanyaan_terakhir"] = pertanyaan

    # Edukasi awal
    if not context.user_data.get("sudah_diedukasi"):
        await update.message.reply_text(
            "📌 *Panduan Interaksi Bot:*\n"
            "Silakan ajukan pertanyaan.\n"
            "Contoh:\n- _Siapa santri dengan hafalan terbanyak?_\n- _Tolong tampilkan rekap bulan Juli._",
            parse_mode="Markdown"
        )
        context.user_data["sudah_diedukasi"] = True

    # Kirim pertanyaan: apakah ini terkait pondok?
    keyboard = [
        [
            InlineKeyboardButton("✅ Ya", callback_data="pertanyaan_pondok_ya"),
            InlineKeyboardButton("❌ Tidak", callback_data="pertanyaan_pondok_tidak"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤔 *Apakah pertanyaan ini berkaitan dengan PPTQ AL-ITQON GOWA?*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# Callback untuk tombol Ya / Tidak
async def handle_pertanyaan_konfirmasi(update, context):
    query = update.callback_query
    await query.answer()
    pilihan = query.data
    pertanyaan = context.user_data.get("pertanyaan_terakhir", "").lower()

    if pilihan == "pertanyaan_pondok_ya":
        # 1. Handler manual
        manual = cari_manual_berdasarkan_pertanyaan(pertanyaan)
        if manual:
            await query.edit_message_text(manual[:4096], parse_mode="Markdown")
            return

        # 2. Cek rekap
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
        return

    elif pilihan == "pertanyaan_pondok_tidak":
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
        loading_msg = await query.message.reply_text("🤖 Saya sedang mencari jawaban terbaik...")
        jawaban = tanyakan_ke_model(pertanyaan)
        await loading_msg.delete()
        await query.message.reply_text(jawaban[:4096], parse_mode="Markdown")
        return
