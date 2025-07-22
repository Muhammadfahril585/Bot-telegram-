from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    CallbackQueryHandler
)
from utils.gsheet import get_sheet
from datetime import datetime
from lib.rekap import kirim_rekap_pekanan

# Tahapan dalam Conversation
PILIH_HALQ, PILIH_SANTRI, PILIH_STATUS, INPUT_HALAMAN, INPUT_JUZ = range(5)

# Simpan data laporan sementara di memory user_data
async def start_lapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Daftar halaqah (contoh)
    halaqah_list = get_halaqah_list()
    buttons = [[InlineKeyboardButton(h, callback_data=f"HALQ|{h}")] for h in halaqah_list]
    await update.message.reply_text(
        "📌 Pilih halaqah:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return PILIH_HALQ

async def pilih_halaqah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, nama_halaqah = query.data.split("|")
    context.user_data["halaqah"] = nama_halaqah

    # Ambil daftar santri dari halaqah
    santri_list = get_santri_by_halaqah(nama_halaqah)
    context.user_data["santri_list"] = santri_list
    context.user_data["index"] = 0
    return await tampilkan_santri(update, context)

async def tampilkan_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data["index"]
    santri = context.user_data["santri_list"][index]
    context.user_data["santri"] = santri

    buttons = [
        [InlineKeyboardButton("📖 Hafalan Baru", callback_data="STATUS|hafalan")],
        [InlineKeyboardButton("📘 Tahsin", callback_data="STATUS|tahsin")],
        [InlineKeyboardButton("📝 Ujian", callback_data="STATUS|ujian")],
        [InlineKeyboardButton("📚 Sima'an", callback_data="STATUS|simaan")],
        [InlineKeyboardButton("🤒 Sakit", callback_data="STATUS|sakit")],
        [InlineKeyboardButton("📆 Izin", callback_data="STATUS|izin")],
        [InlineKeyboardButton("🔁 Muroja'ah", callback_data="STATUS|murojaah")]
    ]
    await update.callback_query.edit_message_text(
        f"🧕 Nama Santri: *{santri}*\n\nPilih status laporan:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return PILIH_STATUS

async def pilih_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, status = query.data.split("|")
    context.user_data["status"] = status

    if status == "hafalan":
        return await tampilkan_halaman(update)
    elif status == "tahsin":
        return await tampilkan_halaman(update)
    elif status in ["ujian", "simaan", "murojaah"]:
        return await tampilkan_juz(update)
    elif status == "sakit":
        simpan_data("sakit", context)
        return await lanjut_ke_santri_berikutnya(update, context)
    elif status == "izin":
        simpan_data("izin", context)
        return await lanjut_ke_santri_berikutnya(update, context)

async def tampilkan_halaman(update: Update):
    tombol = [
        [InlineKeyboardButton(str(i), callback_data=f"HAL|{i}") for i in range(1, 6)],
        [InlineKeyboardButton(str(i), callback_data=f"HAL|{i}") for i in range(6, 11)],
    ]
    await update.callback_query.edit_message_text(
        "📄 Masukkan jumlah halaman hafalan baru:",
        reply_markup=InlineKeyboardMarkup(tombol)
    )
    return INPUT_HALAMAN

async def input_halaman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, halaman = query.data.split("|")
    context.user_data["halaman"] = int(halaman)
    return await tampilkan_juz(update)

async def tampilkan_juz(update: Update):
    tombol = []
    for i in range(1, 31):
        tombol.append(InlineKeyboardButton(str(i), callback_data=f"JUZ|{i}"))
    # Susun 6 tombol per baris
    rows = [tombol[i:i + 6] for i in range(0, len(tombol), 6)]
    await update.callback_query.edit_message_text(
        "🕌 Masukkan nomor Juz:",
        reply_markup=InlineKeyboardMarkup(rows)
    )
    return INPUT_JUZ

async def input_juz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, juz = query.data.split("|")
    status = context.user_data["status"]
    if status == "hafalan":
        context.user_data["juz"] = juz
        simpan_data("hafalan", context)
    elif status == "tahsin":
        context.user_data["juz"] = juz
        simpan_data("tahsin", context)
    elif status == "ujian":
        simpan_data("ujian", context, juz)
    elif status == "simaan":
        simpan_data("simaan", context, juz)
    elif status == "murojaah":
        simpan_data("murojaah", context, juz)
    return await lanjut_ke_santri_berikutnya(update, context)

async def lanjut_ke_santri_berikutnya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["index"] += 1
    if context.user_data["index"] >= len(context.user_data["santri_list"]):
        await update.callback_query.edit_message_text(
            "✅ Semua laporan berhasil dicatat.\nInsyaAllah rekap akan dikirim kembali.",
            reply_markup=None
        )
        chat_id = update.effective_chat.id if update.effective_chat else update.callback_query.message.chat_id
        await kirim_rekap_pekanan(update=update, context=context, chat_id=chat_id)

        return ConversationHandler.END
    else:
        return await tampilkan_santri(update, context)

def kolom_ke_indeks(kolom):
    """Konversi huruf kolom Excel (misalnya 'A', 'N') ke nomor indeks (1-based)."""
    kolom = kolom.upper()
    indeks = 0
    for i, huruf in enumerate(reversed(kolom)):
        indeks += (ord(huruf) - 64) * (26 ** i)
    return indeks

def simpan_data(jenis, context, value=None):
    sheet = get_sheet("Santri")
    halaqah = context.user_data["halaqah"]
    nama_santri = context.user_data["santri"]

    # Pemetaan jenis laporan ke kolom
    jenis_map = {
        "hafalan": "F",
        "tahsin": "G",
        "ujian": "H",
        "simaan": "I",
        "sakit": "J",
        "izin": "K",
        "murojaah": "L"
    }

    # Deteksi waktu
    now = datetime.now()
    bulan_map = {
        "January": "Januari", "February": "Februari", "March": "Maret",
        "April": "April", "May": "Mei", "June": "Juni",
        "July": "Juli", "August": "Agustus", "September": "September",
        "October": "Oktober", "November": "November", "December": "Desember"
    }
    bulan = bulan_map[now.strftime("%B")]
    pekan_ke = (now.day - 1) // 7 + 1

    data = sheet.get_all_values()
    target_row = None
    in_block = False

    # Temukan baris nama santri di halaqah yang aktif
    for i, row in enumerate(data):
        if row and "Halaqah" in row[0] and row[0].strip() == halaqah.strip():
            in_block = True
            continue
        if in_block and row and "Halaqah" in row[0]:
            break
        if in_block and row and row[0].strip().lower() == nama_santri.strip().lower():
            target_row = i + 1
            break

    if not target_row:
        print(f"[❌] Baris santri '{nama_santri}' tidak ditemukan di halaqah '{halaqah}'")
        return

    # Tulis kolom pekan & bulan
    sheet.update_acell(f"D{target_row}", f"Pekan {pekan_ke}")
    sheet.update_acell(f"E{target_row}", bulan)

    kolom = jenis_map.get(jenis)
    if not kolom:
        print(f"[❌] Jenis laporan tidak dikenali: {jenis}")
        return

    # Tentukan nilai yang akan ditulis
    if jenis == "hafalan":
        halaman = int(context.user_data.get("halaman") or 0)
        juz = context.user_data.get("juz", "?")
        nilai = f"{halaman} Halaman - Juz {juz}"
        # Simpan status tercapai/tidak ke kolom L
        keterangan_col = "M"
        keterangan = "Tercapai" if halaman >= 3 else "Tidak tercapai"
        sheet.update_acell(f"{keterangan_col}{target_row}", keterangan)

        # Update kolom Total (N)
        kolom_total = "N"
        indeks_total = kolom_ke_indeks(kolom_total)
        current_total = sheet.cell(target_row, indeks_total).value or "0"

        try:
            total_int = int(current_total.strip())
        except ValueError:
            total_int = 0

        new_total = total_int + halaman
        sheet.update_cell(target_row, indeks_total, str(new_total))

    elif jenis == "tahsin":
        halaman = int(context.user_data.get("halaman") or 0)
        juz = context.user_data.get("juz", "?")
        nilai = f"{halaman} Halaman - Juz {juz}"
        sheet.update_acell(f"M{target_row}", "Tahsin")

        # Update kolom Total (N)
        sheet.update_acell(f"N{target_row}", f"{halaman} Halaman")

    elif jenis == "ujian":
        nilai = f"Juz {value or '?'}"
        sheet.update_acell(f"{kolom}{target_row}", nilai)
        sheet.update_acell(f"M{target_row}", "Persiapan Ujian")

    elif jenis == "simaan":
        nilai = f"{value or '?'} Juz"
        sheet.update_acell(f"{kolom}{target_row}", nilai)
        sheet.update_acell(f"M{target_row}", "Persiapan Sima'an")

    elif jenis == "murojaah":
        nilai = f"Juz {value or '?'}"
        sheet.update_acell(f"{kolom}{target_row}", nilai)
        sheet.update_acell(f"M{target_row}", "Muroja'ah")

    elif jenis == "sakit":
        nilai = "Sakit"
        sheet.update_acell(f"{kolom}{target_row}", nilai)
        sheet.update_acell(f"M{target_row}", "Sakit")

    elif jenis == "izin":
        nilai = "Izin"
        sheet.update_acell(f"{kolom}{target_row}", nilai)
        sheet.update_acell(f"M{target_row}", "Izin")

    else:
        nilai = "-"
        sheet.update_acell(f"{kolom}{target_row}", nilai)
# Dummy fungsi pengganti
def get_halaqah_list():
    """Mengambil daftar halaqah dari baris kedua"""
    sheet = get_sheet("Santri")
    values = sheet.get_all_values()

    daftar_halaqah = []

    # Ambil dari baris kedua (indeks 1) karena baris pertama adalah "Daftar Santri"
    for i in range(1, len(values)):
        baris = values[i]
        if baris and "Halaqah" in baris[0]:
            nama_halaqah = baris[0].strip()
            daftar_halaqah.append(nama_halaqah)
      return daftar_halaqah if daftar_halaqah else ["Halaqah 1", "Halaqah 2"]

def get_santri_by_halaqah(nama_halaqah):
    """Mengambil santri dengan struktur spesifik"""
    sheet = get_sheet("Santri")
    values = sheet.get_all_values()

    santri = []
    target_section = False

    for i, baris in enumerate(values):
        # Cari baris halaqah (dimulai dari baris kedua)
        if i >= 1 and baris and "Halaqah" in baris[0] and nama_halaqah == baris[0].strip():
            target_section = True
            continue

        # Jika sudah menemukan section yang benar
        if target_section:
            # Stop jika menemukan halaqah berikutnya
            if baris and "Halaqah" in baris[0]:
                break

            # Skip baris header (baris setelah halaqah adalah header kolom)
            if i >= 3 and baris and baris[0].strip() and baris[0].strip() != "Nama Santri":
                santri.append(baris[0].strip())

            # Batasan maksimal 13 santri per halaqah
            if len(santri) >= 13:
                break

    return santri if santri else ["Ahmad", "Fatimah", "Ali"]
# Conversation handler
laporan_pekanan_conv = ConversationHandler(
    entry_points=[CommandHandler("lapor", start_lapor)],
    states={
        PILIH_HALQ: [CallbackQueryHandler(pilih_halaqah, pattern=r"^HALQ\|")],
        PILIH_STATUS: [CallbackQueryHandler(pilih_status, pattern=r"^STATUS\|")],
        INPUT_HALAMAN: [CallbackQueryHandler(input_halaman, pattern=r"^HAL\|")],
        INPUT_JUZ: [CallbackQueryHandler(input_juz, pattern=r"^JUZ\|")]
    },
    fallbacks=[],
    allow_reentry=True
)
