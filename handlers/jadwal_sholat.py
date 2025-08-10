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
    payload = {"wilayah": KOTA_ID[kota]}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.post(url, data=payload, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal ambil data: {e}")
        return

    soup = BeautifulSoup(res.text, "html.parser")

    # Ambil judul bulan hijriah
    judul = soup.find("font", style=lambda v: v and "font-size:16px" in v)
    if judul:
        judul_text = judul.get_text(strip=True)
    else:
        judul_text = f"Jadwal Shalat Bulanan - {kota.capitalize()}"

    # Ambil tabel jadwal
    table = soup.find("table", class_="table-bordered")
    if not table:
        await update.message.reply_text("⚠️ Jadwal tidak ditemukan.")
        return

    hari_list = []
    for tr in table.find("tbody").find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cols) == 7:
            tanggal, magrib, isya, subuh, duha, zuhur, asar = cols
            teks_hari = (
                f"{tanggal}\n"
                f"🌅 Subuh : {subuh}\n"
                f"🌞 Duha  : {duha}\n"
                f"🏙 Zuhur : {zuhur}\n"
                f"🌇 Asar  : {asar}\n"
                f"🌆 Maghrib : {magrib}\n"
                f"🌃 Isya : {isya}\n"
                "────────────────\n"
            )
            hari_list.append(teks_hari)

    # Bagi menjadi dua bagian jika lebih dari 15 hari
    if len(hari_list) > 15:
        part1 = "".join(hari_list[:15])
        part2 = "".join(hari_list[15:])

        await update.message.reply_text(f"📅 *{judul_text}* - {kota.capitalize()}\n\n{part1}", parse_mode="Markdown")
        await update.message.reply_text(part2, parse_mode="Markdown")
    else:
        hasil = "".join(hari_list)
        await update.message.reply_text(f"📅 *{judul_text}* - {kota.capitalize()}\n\n{hasil}", parse_mode="Markdown")
