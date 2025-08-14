from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from utils.gsheet import get_sheet

# ================== KONFIGURASI ==================
NAMA_SHEET = "DATA_SANTRI"
PASSWORD_BOT = "AL2020"
# State
INPUT_PASSWORD, SHOW_DATA = range(2)
# =================================================

async def _show_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sheet = get_sheet(NAMA_SHEET)
    rows = sheet.get_all_values()[2:]  # Ambil data mulai baris ke-3

    daftar_nama = []
    total_alumni = 0
    for row in rows:
        # Kolom status/alumni: indeks 31 (AE) pada kode kamu
        is_alumni = row[31].strip().lower() == "alumni" if len(row) > 31 else False
        if is_alumni:
            total_alumni += 1
            continue  # Jangan ditampilkan

        nama = row[2] if len(row) > 2 else "Tanpa Nama"
        daftar_nama.append(nama)

    total_aktif = len(daftar_nama)

    pesan = f"📋 *Daftar Santri Aktif di PPTQ AL-ITQON GOWA*\n"
    pesan += f"Total: *{total_aktif} santri aktif* | *{total_alumni} Alumni*\n\n"

    # (Hati-hati: jika data sangat banyak, Telegram bisa membatasi panjang pesan)
    MAX_LEN = 3900
    body = ""
    for i, nama in enumerate(daftar_nama, 1):
        line = f"{i}. {nama}\n"
        if len(pesan) + len(body) + len(line) > MAX_LEN:
            break
        body += line

    await update.message.reply_text(pesan + body, parse_mode="Markdown")

# ====== Conversation: minta password dulu ======
async def lihat_semua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔑 Masukkan *kata sandi* untuk melihat *Daftar Santri Aktif*:", parse_mode="Markdown")
    return INPUT_PASSWORD
    
async def admin_entry_lihat_semua(update, context):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("🔑 Masukkan *kata sandi* untuk melihat *Daftar Santri Aktif*:", parse_mode="Markdown")
    return INPUT_PASSWORD
    
async def cek_password_lihat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pwd = (update.message.text or "").strip()
    if pwd != PASSWORD_BOT:
        await update.message.reply_text("❌ Kata sandi *salah*. Akses ditolak.", parse_mode="Markdown")
        return ConversationHandler.END

    context.user_data["verified_lihat_semua"] = True
    await _show_all(update, context)
    return ConversationHandler.END

# ====== Helper untuk mendaftarkan handler ke Application ======
def build_lihat_semua_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("lihat_semua", lihat_semua),
            CallbackQueryHandler(admin_entry_lihat_semua, pattern=r"^admin:lihat_semua$"),  # ⬅️ ini
        ],
        states={
            INPUT_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, cek_password_lihat)],
        },
        fallbacks=[],
        name="lihat_semua_conv",
        persistent=False,
    )
