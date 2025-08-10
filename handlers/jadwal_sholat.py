# handlers/jadwal_sholat.py
import requests
from bs4 import BeautifulSoup
from telegram import Update
from datetime import datetime
from telegram.ext import ContextTypes

KOTA_ID = {
    "luwuk": 341,
    "makassar": 316,
    "jakarta": 88
}

async def jadwal_sholat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Contoh: /jadwal makassar")
        return

    kota = context.args[0].lower()
    if kota not in KOTA_ID:
        await update.message.reply_text(
            f"⚠️ Kota '{kota}' tidak ada.\nPilih: {', '.join(KOTA_ID.keys())}"
        )
        return

    url = "https://krfdsawi.stiba.ac.id/domain/krfdsawi.stiba.ac.id/halaman_jadwal/jadwal_imsakiyah_proses.php"
    payload = {"wilayah": KOTA_ID[kota]}  # sesuai payload di devtools
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal ambil data: {e}")
        return

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", class_="table-bordered")
    if not table:
        await update.message.reply_text("⚠️ Jadwal tidak ditemukan.")
        return

    # Ambil header
    headers_row = [th.get_text(strip=True) for th in table.find_all("th")]
    # Ambil isi tabel
    body_rows = []
    for tr in table.find("tbody").find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        body_rows.append(cols)

    # Format rapi
    hasil = f"📅 *Jadwal Sholat Bulanan - {kota.capitalize()}*\n"
    hasil += "══════════════════════════════\n"
    hasil += " | ".join(headers_row) + "\n"
    hasil += "──────────────────────────────\n"
    for row in body_rows:
        hasil += " | ".join(row) + "\n"

    await update.message.reply_text(hasil, parse_mode="Markdown")
