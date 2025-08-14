from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    CallbackQueryHandler
)
from utils.gsheet import get_sheet
from datetime import datetime
from lib.rekap import kirim_rekap_pekanan
import telegram  # untuk telegram.error.BadRequest

# ================== KONFIG ==================
PASSWORD_BOT = "AL2020"
# Tahapan dalam Conversation (tambahkan INPUT_PASSWORD di depan)
INPUT_PASSWORD, PILIH_HALQ, PILIH_SANTRI, PILIH_STATUS, INPUT_HALAMAN, INPUT_JUZ, INPUT_STATUS_FINAL = range(7)
# ============================================

# ====== STEP 0: minta & cek sandi ======
async def minta_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔑 Masukkan *kata sandi* untuk memulai laporan pekanan:", parse_mode="Markdown")
    return INPUT_PASSWORD

async def admin_entry_lapor(update, context):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("🔑 Masukkan *kata sandi* untuk memulai laporan pekanan:", parse_mode="Markdown")
    return INPUT_PASSWORD
    
async def cek_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pwd = (update.message.text or "").strip()
    if pwd != PASSWORD_BOT:
        await update.message.reply_text("❌ Kata sandi *salah*. Akses ditolak.", parse_mode="Markdown")
        return ConversationHandler.END

    context.user_data["verified_lapor"] = True
    # Lanjut ke flow awal: pilih halaqah
    return await start_lapor(update, context)
# =======================================

# Simpan data laporan sementara di memory user_data
async def start_lapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_lapor"):
        # Guard jika user lompat langsung ke handler ini
        await update.message.reply_text("🔒 Akses dikunci. Ketik /lapor lagi dan masukkan kata sandi.")
        return ConversationHandler.END

    # Daftar halaqah (contoh)
    halaqah_list = get_halaqah_list()
    buttons = [[InlineKeyboardButton(h, callback_data=f"HALQ|{h}")] for h in halaqah_list]
    await update.message.reply_text(
        "📌 Pilih halaqah:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return PILIH_HALQ

async def pilih_halaqah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_lapor"):
        await update.callback_query.edit_message_text("🔒 Akses dikunci. Ketik /lapor lagi dan masukkan kata sandi.")
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()
    _, nama_halaqah = query.data.split("|")
    context.user_data["halaqah"] = nama_halaqah

    # Simpan ID pesan tombol halaqah agar bisa dihapus nanti
    context.user_data["halaqah_message_id"] = query.message.message_id

    # Cek apakah perlu reset, jika tidak lanjut
    should_continue = await cek_dan_tawarkan_reset(update, context)
    if not should_continue:
        return ConversationHandler.END

    # Ambil daftar santri dari halaqah
    santri_list = get_santri_by_halaqah(nama_halaqah)
    context.user_data["santri_list"] = santri_list
    context.user_data["index"] = 0
    return await tampilkan_santri(update, context)

async def tampilkan_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_lapor"):
        await (update.callback_query or update.message).edit_message_text("🔒 Akses dikunci. Ketik /lapor lagi dan masukkan kata sandi.")
        return ConversationHandler.END

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
    try:
        await update.callback_query.edit_message_text(
            f"🧑‍🎓 Nama Santri: *{santri}*\n\nPilih status laporan:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except telegram.error.BadRequest as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise

    return PILIH_STATUS

async def pilih_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_lapor"):
        await update.callback_query.edit_message_text("🔒 Akses dikunci. Ketik /lapor lagi dan masukkan kata sandi.")
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()
    _, status = query.data.split("|")
    context.user_data["status"] = status

    if status in ["hafalan", "tahsin"]:
        return await tampilkan_halaman(update)
    elif status in ["ujian", "simaan", "murojaah"]:
        return await tampilkan_juz(update)
    elif status in ["sakit", "izin"]:
        simpan_data(status, context)
        return await lanjut_ke_santri_berikutnya(update, context)

async def tampilkan_halaman(update: Update):
    tombol = [
        [InlineKeyboardButton(str(i), callback_data=f"HAL|{i}") for i in range(1, 6)],
        [InlineKeyboardButton(str(i), callback_data=f"HAL|{i}") for i in range(6, 11)],
        [InlineKeyboardButton(str(i), callback_data=f"HAL|{i}") for i in range(11, 16)],
        [InlineKeyboardButton(str(i), callback_data=f"HAL|{i}") for i in range(16, 21)],
    ]

    await update.callback_query.edit_message_text(
        "📄 Masukkan jumlah halaman hafalan baru/Tahsin:",
        reply_markup=InlineKeyboardMarkup(tombol)
    )
    return INPUT_HALAMAN

async def input_halaman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_lapor"):
        await update.callback_query.edit_message_text("🔒 Akses dikunci. Ketik /lapor lagi dan masukkan kata sandi.")
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()
    _, halaman = query.data.split("|")
    context.user_data["halaman"] = int(halaman)
    return await tampilkan_juz(update)

async def tampilkan_juz(update: Update):
    tombol = []
    for i in range(1, 31):
        tombol.append(InlineKeyboardButton(str(i), callback_data=f"JUZ|{i}"))
    rows = [tombol[i:i + 6] for i in range(0, len(tombol), 6)]
    await update.callback_query.edit_message_text(
        "🕌 Masukkan nomor Juz:",
        reply_markup=InlineKeyboardMarkup(rows)
    )
    return INPUT_JUZ

async def input_juz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_lapor"):
        await update.callback_query.edit_message_text("🔒 Akses dikunci. Ketik /lapor lagi dan masukkan kata sandi.")
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()
    _, juz = query.data.split("|")
    context.user_data["juz"] = juz
    status = context.user_data["status"]

    if status in ["ujian", "simaan"]:
        tombol = [
            [InlineKeyboardButton("✅ Lulus", callback_data="FINAL|lulus")],
            [InlineKeyboardButton("📖 Persiapan", callback_data="FINAL|persiapan")]
        ]
        await query.edit_message_text(
            f"📋 Status akhir untuk {status} Juz {juz}?\n\nSilakan pilih:",
            reply_markup=InlineKeyboardMarkup(tombol)
        )
        return INPUT_STATUS_FINAL

    elif status in ["hafalan", "tahsin"]:
        simpan_data(status, context)
        return await lanjut_ke_santri_berikutnya(update, context)

    elif status == "murojaah":
        simpan_data("murojaah", context, value=juz)
        return await lanjut_ke_santri_berikutnya(update, context)

    else:
        await query.edit_message_text("Status tidak dikenali. Silakan mulai ulang.")
        return ConversationHandler.END
async def input_status_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_lapor"):
        await update.callback_query.edit_message_text("🔒 Akses dikunci. Ketik /lapor lagi dan masukkan kata sandi.")
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()
    _, hasil = query.data.split("|")
    status = context.user_data["status"]
    juz = context.user_data["juz"]

    if status == "ujian":
        context.user_data["hasil_ujian"] = hasil
        sheet_status = "Lulus Ujian" if hasil == "lulus" else "Persiapan Ujian"
        simpan_data("ujian", context, value=juz)
        sheet = get_sheet("Santri")
        halaqah = context.user_data["halaqah"]
        nama_santri = context.user_data["santri"]
        data = sheet.get_all_values()
        in_block = False
        for i, row in enumerate(data):
            if row and "Halaqah" in row[0] and row[0].strip() == halaqah.strip():
                in_block = True
                continue
            if in_block and row and "Halaqah" in row[0]:
                break
            if in_block and row and row[0].strip().lower() == nama_santri.strip().lower():
                target_row = i + 1
                break
        sheet.update_acell(f"M{target_row}", sheet_status)

    elif status == "simaan":
        sheet_status = "Lulus Sima'an" if hasil == "lulus" else "Persiapan Sima'an"
        simpan_data("simaan", context, value=juz)
        sheet = get_sheet("Santri")
        halaqah = context.user_data["halaqah"]
        nama_santri = context.user_data["santri"]
        data = sheet.get_all_values()
        in_block = False
        for i, row in enumerate(data):
            if row and "Halaqah" in row[0] and row[0].strip() == halaqah.strip():
                in_block = True
                continue
            if in_block and row and "Halaqah" in row[0]:
                break
            if in_block and row and row[0].strip().lower() == nama_santri.strip().lower():
                target_row = i + 1
                break
        sheet.update_acell(f"M{target_row}", sheet_status)

    return await lanjut_ke_santri_berikutnya(update, context)

async def lanjut_ke_santri_berikutnya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_lapor"):
        await update.callback_query.edit_message_text("🔒 Akses dikunci. Ketik /lapor lagi dan masukkan kata sandi.")
        return ConversationHandler.END

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
    return ord(kolom.upper()) - ord("A") + 1

def simpan_data(jenis, context, value=None):
    sheet = get_sheet("Santri")
    halaqah = context.user_data["halaqah"]
    nama_santri = context.user_data["santri"]

    jenis_map = {
        "hafalan": "F",
        "tahsin": "G",
        "ujian": "H",
        "simaan": "I",
        "sakit": "J",
        "izin": "K",
        "murojaah": "L"
    }

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

    sheet.update_acell(f"D{target_row}", f"Pekan {pekan_ke}")
    sheet.update_acell(f"E{target_row}", bulan)

    kolom = jenis_map.get(jenis)
    if not kolom:
        print(f"[❌] Jenis laporan tidak dikenali: {jenis}")
        return

    if jenis == "hafalan":
        halaman = int(context.user_data.get("halaman") or 0)
        juz = context.user_data.get("juz", "?")
        nilai = f"{halaman} Halaman - Juz {juz}"

        sheet.update_acell(f"{kolom}{target_row}", nilai)
        keterangan = "Tercapai" if halaman >= 3 else "Tidak tercapai"
        sheet.update_acell(f"M{target_row}", keterangan)

        indeks_total = kolom_ke_indeks("N")
        current_total = sheet.cell(target_row, indeks_total).value or "0"
        try:
            total_int = int(current_total.strip().split()[0])
        except ValueError:
            total_int = 0
        new_total = total_int + halaman
        sheet.update_cell(target_row, indeks_total, f"{new_total} Halaman")

    elif jenis == "tahsin":
        halaman = int(context.user_data.get("halaman") or 0)
        juz = context.user_data.get("juz", "?")
        nilai = f"{halaman} Halaman - Juz {juz}"

        sheet.update_acell(f"{kolom}{target_row}", nilai)
        sheet.update_acell(f"M{target_row}", "Tahsin")

        indeks_total = kolom_ke_indeks("N")
        current_total = sheet.cell(target_row, indeks_total).value or "0"
        try:
            total_int = int(current_total.strip().split()[0])
        except ValueError:
            total_int = 0
        new_total = total_int + halaman
        sheet.update_cell(target_row, indeks_total, f"{new_total} Halaman")

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
    sheet = get_sheet("Santri")
    values = sheet.get_all_values()
    daftar_halaqah = []
    for i in range(1, len(values)):
        baris = values[i]
        if baris and "Halaqah" in baris[0]:
            nama_halaqah = baris[0].strip()
            daftar_halaqah.append(nama_halaqah)
    return daftar_halaqah if daftar_halaqah else ["Halaqah 1", "Halaqah 2"]

def get_santri_by_halaqah(nama_halaqah):
    sheet = get_sheet("Santri")
    values = sheet.get_all_values()
    santri = []
    target_section = False
    for i, baris in enumerate(values):
        if i >= 1 and baris and "Halaqah" in baris[0] and nama_halaqah == baris[0].strip():
            target_section = True
            continue
        if target_section:
            if baris and "Halaqah" in baris[0]:
                break
            if i >= 3 and baris and baris[0].strip() and baris[0].strip() != "Nama Santri":
                santri.append(baris[0].strip())
            if len(santri) >= 13:
                break
    return santri if santri else ["Ahmad", "Fatimah", "Ali"]

# Fungsi untuk mengecek dan menawarkan reset data pekan
async def cek_dan_tawarkan_reset(update, context):
    if not context.user_data.get("verified_lapor"):
        await (update.message or update.callback_query.message).reply_text("🔒 Akses dikunci. Ketik /lapor lagi dan masukkan kata sandi.")
        return False

    halaqah = context.user_data.get("halaqah")
    sheet = get_sheet("Santri")
    data = sheet.get_all_values()

    now = datetime.now()
    bulan_map = {
        "January": "Januari", "February": "Februari", "March": "Maret",
        "April": "April", "May": "Mei", "June": "Juni",
        "July": "Juli", "August": "Agustus", "September": "September",
        "October": "Oktober", "November": "November", "December": "Desember"
    }
    bulan = bulan_map[now.strftime("%B")]
    pekan_ke = (now.day - 1) // 7 + 1
    teks_pekan = f"Pekan {pekan_ke}"

    in_block = False
    data_sudah_ada = False

    for i, row in enumerate(data):
        if row and "Halaqah" in row[0] and row[0].strip() == halaqah:
            in_block = True
            continue
        if in_block and row and "Halaqah" in row[0]:
            break
        if in_block and row and len(row) > 4 and row[3] == teks_pekan and row[4] == bulan:
            data_sudah_ada = True
            break

    if data_sudah_ada:
        context.user_data["pekan_aktif"] = teks_pekan
        keyboard = [
            [
                InlineKeyboardButton("✅ Ya, reset", callback_data="reset_ya"),
                InlineKeyboardButton("❌ Tidak", callback_data="reset_tidak")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await (update.message or update.callback_query.message).reply_text(
            f"📋 Data untuk *{teks_pekan}* bulan *{bulan}* pada halaqah *{halaqah}* sudah ada.\n"
            "Apakah Anda ingin *menghapus semua data pekan ini* dan membuat laporan baru?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return False
    else:
        return True

async def handle_reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("verified_lapor"):
        await update.callback_query.edit_message_text("🔒 Akses dikunci. Ketik /lapor lagi dan masukkan kata sandi.")
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()

    if query.data == "reset_ya":
        halaqah = context.user_data.get("halaqah")
        sheet = get_sheet("Santri")
        data = sheet.get_all_values()

        now = datetime.now()
        bulan_map = {
            "January": "Januari", "February": "Februari", "March": "Maret",
            "April": "April", "May": "Mei", "June": "Juni",
            "July": "Juli", "August": "Agustus", "September": "September",
            "October": "Oktober", "November": "November", "December": "Desember"
        }
        bulan = bulan_map[now.strftime("%B")]
        pekan_ke = (now.day - 1) // 7 + 1
        teks_pekan = f"Pekan {pekan_ke}"

        in_block = False
        for i, row in enumerate(data):
            if row and "Halaqah" in row[0] and row[0].strip() == halaqah:
                in_block = True
                continue
            if in_block and row and "Halaqah" in row[0]:
                break
            if in_block and row and row[3] == teks_pekan and row[4] == bulan:
                sheet.update(f"D{i+1}:M{i+1}", [["" for _ in range(10)]])  # Kolom D–M

        context.user_data["index"] = 0
        context.user_data["santri_list"] = get_santri_by_halaqah(halaqah)
        context.user_data["santri"] = context.user_data["santri_list"][0]

        halaqah_msg_id = context.user_data.get("halaqah_message_id")
        if halaqah_msg_id:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=halaqah_msg_id
                )
            except Exception as e:
                print("❗ Gagal menghapus pesan halaqah:", e)

        await query.delete_message()
        await context.bot.send_message(
          chat_id=update.effective_chat.id,
          text="✅ *Berhasil direset!*\nSilakan ketik ulang /lapor untuk mulai input data.",
          parse_mode="Markdown"
        )
        return ConversationHandler.END
    else:
        await query.edit_message_text("❌ Reset dibatalkan. Anda bisa melanjutkan pengisian.")
        return ConversationHandler.END

# ====== Conversation handler (dengan sandi) ======
laporan_pekanan_conv = ConversationHandler(
    entry_points=[
        CommandHandler("lapor", minta_password),
        CallbackQueryHandler(admin_entry_lapor, pattern=r"^admin:lapor$"),  # ⬅️ ini
    ],
    states={
        INPUT_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, cek_password)],
        PILIH_HALQ: [
            CallbackQueryHandler(pilih_halaqah, pattern=r"^HALQ\|"),
            CallbackQueryHandler(handle_reset_callback, pattern=r"^reset_"),
        ],
        PILIH_STATUS: [CallbackQueryHandler(pilih_status, pattern=r"^STATUS\|")],
        INPUT_HALAMAN: [CallbackQueryHandler(input_halaman, pattern=r"^HAL\|")],
        INPUT_JUZ: [CallbackQueryHandler(input_juz, pattern=r"^JUZ\|")],
        INPUT_STATUS_FINAL: [CallbackQueryHandler(input_status_final, pattern=r"^FINAL\|")],
    },
    fallbacks=[],
    allow_reentry=True,
    name="lapor_pekanan_conv",
)
