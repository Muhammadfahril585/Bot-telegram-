from telegram import Update
from telegram.ext import ContextTypes
from utils.gsheet import get_sheet
from datetime import datetime

async def kirim_rekap_pekanan(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id=None):
    sheet = get_sheet("Santri")
    halaqah = context.user_data["halaqah"]
    now = datetime.now()
    bulan_map = {
        "January": "Januari", "February": "Februari", "March": "Maret",
        "April": "April", "May": "Mei", "June": "Juni",
        "July": "Juli", "August": "Agustus", "September": "September",
        "October": "Oktober", "November": "November", "December": "Desember"
    }
    bulan = bulan_map[now.strftime("%B")]
    pekan = (now.day - 1) // 7 + 1

    data = sheet.get_all_values()
    hasil = []
    ustadz = "-"
    in_block = False
    nomor = 1

    for i, row in enumerate(data):
        if row and "Halaqah" in row[0] and row[0].strip() == halaqah.strip():
            in_block = True
            ustadz = row[1] if len(row) > 1 else "-"
            continue
        if in_block and row and "Halaqah" in row[0]:
            break

        if in_block and row and row[0].strip() and row[0].strip() != "Nama Santri":
            nama = row[0].strip()
            hafalan_baru = row[5] if len(row) > 5 else "0"
            tahsin = row[6] if len(row) > 6 else ""
            ujian = row[7] if len(row) > 7 else ""
            simaan = row[8] if len(row) > 8 else ""
            status_asli = row[12] if len(row) > 12 else "-"

            # Total Hafalan (misal kolom M)
            total_hafalan = row[1] if len(row) > 1 else "?"
            rentang_juz = row[2] if len(row) > 2 else "?"

            # Tampilkan hafalan dari kolom yang sesuai
            if status_asli == "Tahsin":
               hafalan_baru = tahsin
            elif status_asli == "Persiapan Ujian":
               hafalan_baru = ujian
            elif status_asli == "Persiapan Sima'an":
               hafalan_baru = simaan
            elif status_asli == "Muroja'ah":
               hafalan_baru = row[11] if len(row) > 11 else ""
            emoji_map = {
             "Tercapai": "✅ Tercapai",
             "Tahsin": "🖊️ Tahsin",
             "Tidak tercapai": "❌ Tidak tercapai",
             "Sakit": "🤒 Sakit",
             "Izin": "📆 Izin",
             "Persiapan Ujian": "📚 Persiapan Ujian",
             "Persiapan Sima'an": "🎯 Persiapan Sima'an",
             "Muroja'ah": "🔁 Muroja'ah",
             "": "♻️ -",
             "-": "♻️ -"
            }

            status = emoji_map.get(status_asli.strip(), f"♻️ {status_asli.strip()}")
            hasil.append(
                f"{nomor}️⃣ {nama}\n"
                f"   📘 Hafalan Baru: {hafalan_baru}\n"
                f"   📌 Status: {status}\n"
                f"   📖 Total Hafalan: {total_hafalan} ({rentang_juz})"
            )
            nomor += 1

    pesan = (
        f"📖 *Rekap Hafalan Pekanan*\n"
        f"👥 Halaqah: {halaqah}\n"
        f"🧑‍🏫 Ustadz: {ustadz}\n"
        f"🗓️ Pekan: {pekan} | 📅 Bulan: {bulan}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        + "\n━━━━━━━━━━━━━━━━━━━━\n".join(hasil) +
        "\n━━━━━━━━━━━━━━━━━━━━\n"
        "✨ Barakallahu fiikum. Semangat terus dalam menjaga Al-Qur'an!"
    )

    await context.bot.send_message(chat_id=chat_id, text=pesan, parse_mode="Markdown")
