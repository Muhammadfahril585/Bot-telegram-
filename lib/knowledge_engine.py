from lib.knowledge_base import cari_manual_berdasarkan_pertanyaan
from lib.ai_fallback import tanyakan_ke_model  # fungsi ke OpenRouter
from lib.ai_sql_engine import buat_sql_dari_pertanyaan, jalankan_query
from lib.rekap_bulanan_ai import ambil_data_rekap_bulanan_santri

# Fungsi bantu ekstraksi sederhana
def ekstrak_info_rekap(pertanyaan):
    bulan_list = [
        "januari", "februari", "maret", "april", "mei", "juni",
        "juli", "agustus", "september", "oktober", "november", "desember"
    ]
    bulan_ditemukan = None
    for b in bulan_list:
        if b in pertanyaan:
            bulan_ditemukan = b
            break

    # Ambil nama santri dari pertanyaan
    nama_santri = None
    kata = pertanyaan.split()
    for i, k in enumerate(kata):
        if k in ("santri", "rekap") and i+1 < len(kata):
            nama_santri = kata[i+1].capitalize()
            break

    return {"bulan": bulan_ditemukan, "santri": nama_santri}

# Fungsi utama
async def proses_pertanyaan_pondok(update, context, pertanyaan):
    chat_id = update.effective_chat.id
    pertanyaan_lower = pertanyaan.lower()

    # Edukasi awal
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
    manual = cari_manual_berdasarkan_pertanyaan(pertanyaan_lower)
    if manual:
        await context.bot.send_message(chat_id=chat_id, text=manual[:4096], parse_mode="Markdown")
        return
        
    # Coba deteksi rekap bulanan dulu
    info = ekstrak_info_rekap(pertanyaan_lower)
    if info["bulan"] and info["santri"]:
        hasil = ambil_data_rekap_bulanan_santri(nama_santri=info["santri"], bulan=info["bulan"])
        await context.bot.send_message(chat_id=chat_id, text=hasil, parse_mode="Markdown")
        return

    # Jika tidak rekap, lempar ke AI SQL
    sql_query = buat_sql_dari_pertanyaan(pertanyaan)
    if sql_query:
        hasil = jalankan_query(sql_query)
        await context.bot.send_message(chat_id=chat_id, text=hasil)
        return

    # Jika semua gagal
    await context.bot.send_message(chat_id=chat_id, text="⚠️ Maaf, saya belum bisa menjawab pertanyaan tersebut.")

async def proses_pertanyaan_umum(update, context, pertanyaan):
    chat_id = update.effective_chat.id

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    jawaban = tanyakan_ke_model(pertanyaan)

    await context.bot.send_message(chat_id=chat_id, text=jawaban[:4096], parse_mode="Markdown")
