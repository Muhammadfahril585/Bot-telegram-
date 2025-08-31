from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from lib.navigation import tombol_rekap_bulanan
from lib.navigation import tombol_navigasi
from utils.gsheet import get_sheet

# Fungsi utama dipanggil dari tombol
async def rekap_bulanan_tombol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    sheet = get_sheet("Santri")
    data = sheet.get_all_values()

    halaqah_set = set()
    for row in data:
        if row and "Halaqah" in row[0]:
            halaqah_set.add(row[0].strip())

    if not halaqah_set:
        await query.edit_message_text("Belum ada halaqah yang tersedia.")
        return

    buttons = [
        [InlineKeyboardButton(halaqah, callback_data=f"REKAP_HALAQAH|{halaqah}")]
        for halaqah in sorted(halaqah_set)
    ]
    await query.edit_message_text(
        "👥 Pilih halaqah untuk rekap bulanan:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Pilih bulan berdasarkan halaqah
async def pilih_bulan_rekap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, halaqah_dipilih = query.data.split("|")

    sheet = get_sheet("Santri")
    data = sheet.get_all_values()

    bulan_set = set()
    inside = False
    for row in data:
        if row and row[0].strip() == halaqah_dipilih:
            inside = True
            continue
        if inside:
            if not row[0].strip() or row[0].strip().lower() == "nama santri":
                continue
            if "halaqah" in row[0].lower():
                break
            if len(row) >= 5:
                bulan_set.add(row[4].strip())

    if not bulan_set:
        await query.edit_message_text("Tidak ditemukan data bulan untuk halaqah ini.")
        return

    context.user_data["halaqah_dipilih"] = halaqah_dipilih

    buttons = [
        [InlineKeyboardButton(bulan, callback_data=f"REKAPBULAN|{bulan}")]
        for bulan in sorted(bulan_set)
    ]
    await query.edit_message_text(
        f"📅 Pilih bulan untuk halaqah *{halaqah_dipilih}*:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Proses rekap bulan (versi yang membolehkan Pekan 1–3 ditampilkan sebagai "sementara")
async def proses_rekap_bulan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, bulan_dipilih = query.data.split("|")
    halaqah_dipilih = context.user_data.get("halaqah_dipilih")

    if not halaqah_dipilih:
        await query.edit_message_text("Terjadi kesalahan: halaqah tidak ditemukan.")
        return

    sheet = get_sheet("Santri")
    data = sheet.get_all_values()

    # 1) Tentukan pekan tertinggi pada bulan & halaqah ini
    inside = False
    pekan_tertinggi = 0
    for row in data:
        if row and row[0].strip() == halaqah_dipilih:
            inside = True
            continue
        if inside:
            if not row[0].strip() or row[0].strip().lower() == "nama santri":
                continue
            if "halaqah" in row[0].lower():
                break
            if len(row) >= 14:
                pekan = row[3].strip()
                bulan = row[4].strip()
                if bulan != bulan_dipilih:
                    continue
                m = re.search(r'(\d+)', pekan)  # ambil angka dari "Pekan 1/2/3/4/5"
                if m:
                    pek = int(m.group(1))
                    if pek > pekan_tertinggi:
                        pekan_tertinggi = pek

    if pekan_tertinggi == 0:
        await query.edit_message_text("Tidak ada data rekap bulan tersebut.")
        return

    # 2) Kumpulkan hasil dari pekan tertinggi yang tersedia
    inside = False
    hasil = []
    for row in data:
        if row and row[0].strip() == halaqah_dipilih:
            inside = True
            continue
        if inside:
            if not row[0].strip() or row[0].strip().lower() == "nama santri":
                continue
            if "halaqah" in row[0].lower():
                break
            if len(row) >= 14:
                nama = row[0].strip()
                pekan = row[3].strip()
                bulan = row[4].strip()
                total = row[13].strip() if len(row) > 13 else "0 Halaman"
                if bulan != bulan_dipilih:
                    continue
                if re.search(rf'\b{pekan_tertinggi}\b', pekan):
                    hasil.append((nama, total))

    if not hasil:
        await query.edit_message_text("Tidak ada data rekap bulan tersebut.")
        return

    # 3) Susun teks (tampilkan label 'sementara' jika pekan tertinggi < 4)
    status_label = ""
    if pekan_tertinggi < 4:
        status_label = f" _(Rekap sementara s.d. Pekan {pekan_tertinggi})_"

    teks = (
        f"📚 *Rekap Hafalan Bulan {bulan_dipilih}*{status_label}\n"
        f"👥 Halaqah: {halaqah_dipilih}\n\n"
    )
    for i, (nama, total) in enumerate(hasil, 1):
        teks += f"{i}. {nama}\n📝 Total Hafalan Baru Bulan Ini: {total}\n\n"

    if pekan_tertinggi < 4:
        teks += (
            "ℹ️ Rekap ini bersifat sementara. Nilai akhir akan ditetapkan setelah "
            "mencapai Pekan 4 (atau Pekan 5 bila ada).\n\n"
        )

    teks += "📌 Jika belum ada tambahan hafalan, tetap semangat! Barakallahu fiikum."

    context.user_data["rekap_bulanan_teks"] = teks
    await query.edit_message_text(
        text=teks,
        parse_mode="Markdown",
        reply_markup=tombol_rekap_bulanan()
            )

import re
from utils.pdf import buat_pdf_rekap_bulanan
from telegram import InputFile

async def handle_buat_pdf_rekap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    teks = context.user_data.get("rekap_bulanan_teks")
    if not teks:
        await query.edit_message_text("⚠️ Tidak ada data rekap untuk dijadikan PDF.")
        return

    # Ambil info bulan dan halaqah dari teks
    match_bulan = re.search(r"Rekap Hafalan Bulan (\w+)", teks)
    match_halaqah = re.search(r"Halaqah: (.+)", teks)

    bulan = match_bulan.group(1) if match_bulan else "Bulan"
    halaqah = match_halaqah.group(1).replace(" ", "_") if match_halaqah else "Halaqah"

    # Nama file PDF dinamis
    nama_file = f"Rekap_{bulan}_{halaqah}.pdf"

    # Buat PDF
    pdf_file = buat_pdf_rekap_bulanan(teks)

    # Kirim PDF
    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=InputFile(pdf_file, filename=nama_file),
        caption=f"📄 Berikut PDF Rekap Hafalan Bulanan: *{bulan}*",
        parse_mode="Markdown"
    )
# Handler list
rekap_bulanan_handlers = [
    CallbackQueryHandler(rekap_bulanan_tombol, pattern="^rekap_bulanan$"),
    CallbackQueryHandler(pilih_bulan_rekap, pattern=r"^REKAP_HALAQAH\|"),
    CallbackQueryHandler(proses_rekap_bulan, pattern=r"^REKAPBULAN\|"),
]
