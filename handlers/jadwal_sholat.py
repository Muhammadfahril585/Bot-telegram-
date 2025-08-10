# handlers/jadwal_sholat.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

# Mapping kota ke ID dari hasil yang kamu berikan
KOTA_ID = {
    "luwuk": 341,
    "makassar": 316,
    "jakarta": 88,
}

async def jadwal_sholat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Pastikan ada argumen kota
    if not context.args:
        await update.message.reply_text("⚠️ Contoh: /jadwal makassar")
        return

    kota = context.args[0].lower()
    if kota not in KOTA_ID:
        await update.message.reply_text(
            f"⚠️ Kota '{kota}' tidak tersedia.\nKota yang tersedia: {', '.join(KOTA_ID.keys())}"
        )
        return

    # Ambil bulan & tahun saat ini
    bulan = datetime.now().month
    tahun = datetime.now().year

    # URL dan data POST
    url = "https://krfdsawi.stiba.ac.id/domain/krfdsawi.stiba.ac.id/halaman_jadwal/jadwal_imsakiyah_proses.php"
    payload = {
        "id_kota": KOTA_ID[kota],
        "bulan": bulan,
        "tahun": tahun
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal mengambil data: {e}")
        return

    # Parsing HTML untuk ambil tabel jadwal
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    if not table:
        await update.message.reply_text("⚠️ Tidak ada data jadwal sholat untuk kota ini.")
        return

    rows = table.find_all("tr")

    # Format hasil
    hasil = f"📅 **Jadwal Sholat {kota.capitalize()} - {bulan}/{tahun}**\n"
    hasil += "════════════════════\n"
    header = [th.get_text(strip=True) for th in rows[0].find_all("th")]
    hasil += " | ".join(header) + "\n"
    hasil += "────────────────────\n"

    for row in rows[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        hasil += " | ".join(cols) + "\n"

    await update.message.reply_text(
        hasil,
        parse_mode="Markdown"
        )
