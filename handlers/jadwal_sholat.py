# handlers/jadwal_sholat.py
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes

KOTA_URL = {
    "makassar": "https://krfdsawi.stiba.ac.id/kota/makassar",
    "jakarta": "https://krfdsawi.stiba.ac.id/kota/jakarta"
}

def get_jadwal_sholat_bulanan(kota: str) -> str:
    kota = kota.lower()
    if kota not in KOTA_URL:
        return "⚠️ Kota tidak tersedia dalam daftar."

    url = KOTA_URL[kota]
    response = requests.get(url)
    if response.status_code != 200:
        return "⚠️ Gagal mengambil data dari situs."

    soup = BeautifulSoup(response.text, "html.parser")
    tabel = soup.find("table")
    if not tabel:
        return "⚠️ Tabel jadwal sholat tidak ditemukan."

    rows = tabel.find_all("tr")
    hasil = f"🕌 *Jadwal Sholat Bulanan* - {kota.title()}\n"
    hasil += "──────────────────────────────\n"
    hasil += "Tgl | Subuh | Zuhur | Ashar | Maghrib | Isya\n"
    hasil += "──────────────────────────────\n"

    for row in rows[1:]:  # Lewati header
        cols = [c.text.strip() for c in row.find_all("td")]
        if len(cols) >= 6:
            tgl, subuh, zuhur, ashar, maghrib, isya = cols[0:6]
            hasil += f"{tgl} | {subuh} | {zuhur} | {ashar} | {maghrib} | {isya}\n"

    return hasil

async def jadwal_sholat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Contoh: /jadwalsholat makassar")
        return

    kota = context.args[0].lower()
    hasil = get_jadwal_sholat_bulanan(kota)
    await update.message.reply_text(hasil, parse_mode="Markdown")
